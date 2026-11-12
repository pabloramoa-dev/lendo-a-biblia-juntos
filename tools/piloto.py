"""Renderiza um episódio do plano, sem tocar em fila nem publicar.

Uso: python -m tools.piloto M001          (manhã do dia 1)
     python -m tools.piloto N001 --so-voz (só a narração)
"""
import json, sys
from estudio import render, roteiro, voz
from src import config
from tools.montar_item import montar

item = montar(sys.argv[1])
trabalho = config.SAIDA / item["id"]
trabalho.mkdir(parents=True, exist_ok=True)
wav = trabalho / "narracao.wav"
tempos = wav.with_suffix(".tempos.json")
if wav.exists() and tempos.exists():
    dados = json.loads(tempos.read_text(encoding="utf-8"))
else:
    dados = voz.gerar(roteiro.montar(item), wav)
print("voz:", dados["voz"], "duracao:", dados["duracao_s"], flush=True)
if "--so-voz" in sys.argv:
    raise SystemExit
destino = config.REELS / f"{item['id']}.mp4"
destino.parent.mkdir(parents=True, exist_ok=True)
render.renderizar(item, wav, dados, destino)
print("PRONTO", destino, flush=True)
