"""Produção diária independente do publicador herdado de outros canais.

Preparar seleciona sem avançar a fila. Confirmar só registra depois de o
GitHub Actions guardar o MP4 validado como artifact.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from tools.montar_item import montar, plano

RAIZ = Path(__file__).resolve().parent.parent
HISTORICO = RAIZ / "conteudo/produzidos.json"
TRABALHO = RAIZ / "output/rotina"
FUSO = ZoneInfo("America/Sao_Paulo")
CRONS = {"0 9 * * *": "manha", "0 21 * * *": "noite"}


def ler(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def gravar(caminho, dados):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporario.replace(caminho)


def periodo_da_execucao(periodo, cron, agora):
    if periodo != "automatico":
        return periodo
    # O evento define o turno mesmo quando o runner começa com atraso.
    if cron:
        if cron not in CRONS:
            raise ValueError(f"Agendamento desconhecido: {cron}")
        return CRONS[cron]
    return "manha" if agora.astimezone(FUSO).hour < 12 else "noite"


def selecionar(episodios, registros, periodo, data):
    if any(r["data_brt"] == data and r["periodo"] == periodo for r in registros):
        return None
    usados = {r["id"] for r in registros}
    pendentes = [e for e in episodios if e["periodo"] == periodo and e["id"] not in usados]
    return min(pendentes, key=lambda e: e["dia"]) if pendentes else None


def validar_item(item):
    if not item["comentado"] or not item["blocos"]:
        raise ValueError(f"{item['id']}: comentário obrigatório ausente")
    if any(not b["versiculos"] or not b["comentario"].strip() for b in item["blocos"]):
        raise ValueError(f"{item['id']}: bloco sem leitura ou comentário")


def saidas(**valores):
    caminho = os.getenv("GITHUB_OUTPUT")
    if caminho:
        with open(caminho, "a", encoding="utf-8") as f:
            for chave, valor in valores.items():
                f.write(f"{chave}={valor}\n")


def preparar(args):
    agora = datetime.now(FUSO)
    periodo = periodo_da_execucao(args.periodo, args.cron, agora)
    data = agora.date().isoformat()
    episodios = list(plano().values())
    if args.modo == "piloto":
        ep = plano()[args.id or ("M001" if periodo == "manha" else "N001")]
        periodo = ep["periodo"]
    else:
        if args.id:
            raise ValueError("Escolha de ID é permitida somente em modo piloto")
        ep = selecionar(episodios, ler(HISTORICO)["registros"], periodo, data)
    if ep is None:
        saidas(produzir="false")
        print("Turno já produzido hoje ou plano do período concluído; nada a repetir.")
        return
    validar_item(montar(ep["id"]))
    job = {"id": ep["id"], "periodo": periodo, "data_brt": data, "modo": args.modo}
    gravar(TRABALHO / "selecionado.json", job)
    nome = f"biblia-{args.modo}-{data}-{periodo}-{ep['id']}"
    saidas(produzir="true", id=ep["id"], artifact=nome)
    print(json.dumps(job, ensure_ascii=False))


def produzir():
    from estudio import render, roteiro, voz
    from src.validar_video import validar

    job = ler(TRABALHO / "selecionado.json")
    item = montar(job["id"])
    validar_item(item)
    destino = TRABALHO / "entrega"
    destino.mkdir(parents=True, exist_ok=True)
    wav = TRABALHO / "narracao.wav"
    dados = voz.gerar(roteiro.montar(item), wav)
    video = destino / f"{item['id']}.mp4"
    render.renderizar(item, wav, dados, video)
    tecnico = validar(video)
    if dados["voz"] == "mudo":
        raise ValueError("Produção diária exige narração real")
    legenda = (f"Dia {item['dia']} · {item['referencia_exibida']}\n\n"
               "Leitura da Bíblia Livre, com explicação em palavras simples.\n\n"
               + (item.get("pergunta", "") + "\n\n" if item.get("pergunta") else "")
               + "Lendo a Bíblia Juntos · @lendoabibliaexplicada\n"
               "#LendoABibliaJuntos #Biblia #PalavraDeDeus\n")
    (destino / "legenda.txt").write_text(legenda, encoding="utf-8")
    meta = {**job, "referencia": item["referencia_exibida"], "dia": item["dia"],
            "voz": dados["voz"], "motor": "Manim + HyperFrames", **tecnico,
            "sha256": hashlib.sha256(video.read_bytes()).hexdigest(),
            "commit_origem": os.getenv("GITHUB_SHA", "local"),
            "gerado_em": datetime.now(FUSO).isoformat(),
            "run_url": (f"https://github.com/{os.getenv('GITHUB_REPOSITORY', '')}/actions/runs/"
                        f"{os.getenv('GITHUB_RUN_ID', '')}")}
    gravar(destino / "episodio.json", meta)
    print(json.dumps(meta, ensure_ascii=False))


def confirmar(args):
    meta = ler(TRABALHO / "entrega/episodio.json")
    if meta["modo"] == "piloto":
        print("Piloto disponível para baixar; sequência diária preservada.")
        return
    if not args.artifact_url or not args.artifact_id:
        raise ValueError("Não registrar antes de o upload do MP4 terminar")
    video = TRABALHO / "entrega" / f"{meta['id']}.mp4"
    if hashlib.sha256(video.read_bytes()).hexdigest() != meta["sha256"]:
        raise ValueError("MP4 diverge do arquivo validado")
    historico = ler(HISTORICO)
    registros = historico["registros"]
    mesmo_turno = [r for r in registros if r["data_brt"] == meta["data_brt"] and r["periodo"] == meta["periodo"]]
    if mesmo_turno:
        if mesmo_turno[0]["sha256"] != meta["sha256"]:
            raise ValueError("Outro vídeo já ocupa esse turno; histórico preservado")
        return
    if any(r["id"] == meta["id"] for r in registros):
        raise ValueError("Episódio já registrado em outro turno")
    registros.append({**meta, "artifact_url": args.artifact_url, "artifact_id": args.artifact_id})
    gravar(HISTORICO, historico)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("acao", choices=["preparar", "produzir", "confirmar"])
    p.add_argument("--periodo", choices=["automatico", "manha", "noite"], default="automatico")
    p.add_argument("--modo", choices=["rotina", "piloto"], default="rotina")
    p.add_argument("--id", default="")
    p.add_argument("--cron", default="")
    p.add_argument("--artifact-url", default="")
    p.add_argument("--artifact-id", default="")
    args = p.parse_args()
    if args.acao == "preparar":
        preparar(args)
    elif args.acao == "produzir":
        produzir()
    else:
        confirmar(args)


if __name__ == "__main__":
    os.chdir(RAIZ)
    main()
