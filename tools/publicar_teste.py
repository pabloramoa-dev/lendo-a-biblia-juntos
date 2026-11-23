"""Teste manual de publicação no @lendoabibliaexplicada.

Uso (dentro do workflow "Publicar teste (manual)"):
    python -m tools.publicar_teste conferir
    python -m tools.publicar_teste publicar --video-url URL --legenda ARQUIVO

Lê IG_USER_ID, IG_ACCESS_TOKEN e IG_GRAPH_BASE do ambiente. O token nunca é
impresso. Antes de publicar, confere se o token aponta para a conta esperada.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

CONTA_ESPERADA = "lendoabibliaexplicada"
ESPERA_S = 10
MAX_TENTATIVAS = 60  # ~10 minutos


def _cfg():
    faltando = [k for k in ("IG_USER_ID", "IG_ACCESS_TOKEN") if not os.getenv(k)]
    if faltando:
        raise SystemExit(f"Segredos ausentes: {faltando}")
    base = (os.getenv("IG_GRAPH_BASE") or "https://graph.facebook.com/v26.0").rstrip("/")
    return base, os.environ["IG_USER_ID"], os.environ["IG_ACCESS_TOKEN"]


def _esconder(texto: str) -> str:
    tok = os.getenv("IG_ACCESS_TOKEN", "")
    return texto.replace(tok, "***TOKEN***") if tok else texto


def _chamar(metodo: str, url: str, campos: dict) -> dict:
    dados = urllib.parse.urlencode(campos).encode()
    if metodo == "GET":
        req = urllib.request.Request(f"{url}?{dados.decode()}")
    else:
        req = urllib.request.Request(url, data=dados, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode(errors="replace")
        raise SystemExit(_esconder(f"Erro da Meta (HTTP {e.code}): {corpo[:800]}")) from None


def conferir() -> dict:
    base, user, tok = _cfg()
    conta = _chamar("GET", f"{base}/{user}",
                    {"fields": "id,username,media_count", "access_token": tok})
    print(json.dumps(conta, ensure_ascii=False))
    if str(conta.get("username", "")).lower() != CONTA_ESPERADA:
        raise SystemExit(f"O token aponta para @{conta.get('username')}, não para @{CONTA_ESPERADA}. Nada publicado.")
    return conta


def publicar(video_url: str, legenda: str) -> dict:
    conferir()
    base, user, tok = _cfg()
    container = _chamar("POST", f"{base}/{user}/media", {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": legenda,
        "share_to_feed": "true",
        "access_token": tok,
    })["id"]
    print(f"Container criado: {container}")

    for _ in range(MAX_TENTATIVAS):
        estado = _chamar("GET", f"{base}/{container}",
                         {"fields": "status_code,status", "access_token": tok})
        codigo = estado.get("status_code")
        print(f"Processamento na Meta: {codigo}")
        if codigo == "FINISHED":
            break
        if codigo in {"ERROR", "EXPIRED"}:
            raise SystemExit(f"A Meta recusou o vídeo: {estado}")
        time.sleep(ESPERA_S)
    else:
        raise SystemExit("A Meta não terminou de processar o vídeo a tempo. Nada publicado.")

    media_id = _chamar("POST", f"{base}/{user}/media_publish",
                       {"creation_id": container, "access_token": tok})["id"]
    info = _chamar("GET", f"{base}/{media_id}", {"fields": "permalink", "access_token": tok})
    resultado = {"media_id": media_id, "permalink": info.get("permalink")}
    print(json.dumps(resultado, ensure_ascii=False))
    saida = os.getenv("GITHUB_OUTPUT")
    if saida:
        with open(saida, "a", encoding="utf-8") as f:
            f.write(f"media_id={media_id}\npermalink={resultado['permalink'] or ''}\n")
    resumo = os.getenv("GITHUB_STEP_SUMMARY")
    if resumo:
        with open(resumo, "a", encoding="utf-8") as f:
            f.write(f"## Reel publicado\n\n{resultado['permalink']}\n")
    return resultado


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("acao", choices=["conferir", "publicar"])
    p.add_argument("--video-url", default="")
    p.add_argument("--legenda", default="")
    a = p.parse_args()
    if a.acao == "conferir":
        conferir()
    else:
        if not a.video_url or not a.legenda:
            raise SystemExit("Informe --video-url e --legenda")
        with open(a.legenda, encoding="utf-8") as f:
            publicar(a.video_url, f.read().strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
