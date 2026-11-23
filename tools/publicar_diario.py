"""Publicação automática no @lendoabibliaexplicada.

    python -m tools.publicar_diario selecionar --periodo manha|noite
    python -m tools.publicar_diario registrar --id N006 --media-id ... --permalink ...

"selecionar" escolhe o episódio de HOJE (horário de Brasília) daquele turno,
já produzido pela rotina, e diz se ele deve ser publicado. Nada é publicado se:
  - PUBLICAR_ATIVO não for "true";
  - o episódio de hoje daquele turno ainda não foi produzido;
  - o episódio já consta em conteudo/publicados_instagram.json.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
PRODUZIDOS = RAIZ / "conteudo/produzidos.json"
PUBLICADOS = RAIZ / "conteudo/publicados_instagram.json"
FUSO = ZoneInfo("America/Sao_Paulo")


def _ler(caminho: Path, padrao):
    return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else padrao


def _saida(**valores):
    destino = os.getenv("GITHUB_OUTPUT")
    linhas = [f"{k}={v}" for k, v in valores.items()]
    if destino:
        with open(destino, "a", encoding="utf-8") as f:
            f.write("\n".join(linhas) + "\n")
    print("\n".join(linhas))


def selecionar(periodo: str, hoje: str | None = None, exigir: bool = False) -> dict | None:
    hoje = hoje or datetime.now(FUSO).date().isoformat()
    if os.getenv("PUBLICAR_ATIVO", "false").strip().lower() != "true":
        aviso = "PUBLICAR_ATIVO não está true: publicação desabilitada."
        if exigir:
            raise SystemExit(aviso)
        print(aviso)
        _saida(publicar="false")
        return None
    publicados = {p["id"] for p in _ler(PUBLICADOS, {"registros": []})["registros"]}
    candidatos = [r for r in _ler(PRODUZIDOS, {"registros": []})["registros"]
                  if r.get("modo") == "rotina" and r.get("periodo") == periodo
                  and r.get("data_brt") == hoje and r.get("artifact_id")]
    if not candidatos:
        aviso = f"FALHA: nenhum episódio de {periodo} produzido hoje ({hoje}). Verificar workflow de produção."
        if exigir:
            raise SystemExit(aviso)
        print(aviso)
        _saida(publicar="false")
        return None
    ep = candidatos[-1]
    if ep["id"] in publicados:
        print(f"{ep['id']} já foi publicado; nada a fazer.")
        _saida(publicar="false")
        return None
    _saida(publicar="true", id=ep["id"], artifact=ep["artifact_id"])
    return ep


def registrar(ep_id: str, media_id: str, permalink: str) -> None:
    dados = _ler(PUBLICADOS, {"versao": 1, "registros": []})
    if any(p["id"] == ep_id for p in dados["registros"]):
        return
    dados["registros"].append({
        "id": ep_id,
        "media_id": media_id,
        "permalink": permalink,
        "publicado_em": datetime.now(FUSO).isoformat(timespec="seconds"),
        "run_url": (f"https://github.com/{os.getenv('GITHUB_REPOSITORY', '')}/actions/runs/"
                    f"{os.getenv('GITHUB_RUN_ID', '')}"),
    })
    tmp = PUBLICADOS.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(PUBLICADOS)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("acao", choices=["selecionar", "registrar"])
    p.add_argument("--periodo", choices=["manha", "noite"])
    p.add_argument("--exigir", action="store_true", help="Falhar quando faltar episódio ou a publicação estiver desativada")
    p.add_argument("--id", default="")
    p.add_argument("--media-id", default="")
    p.add_argument("--permalink", default="")
    a = p.parse_args()
    if a.acao == "selecionar":
        if not a.periodo:
            raise SystemExit("Informe --periodo")
        selecionar(a.periodo, exigir=a.exigir)
    else:
        registrar(a.id, a.media_id, a.permalink)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
