"""Gera uma capa exclusiva para a grade do Instagram, sem alterar o MP4.

Uso: python -m tools.capa_biblia midia/M001.mp4 midia/episodio.json midia/M001.jpg
"""
from __future__ import annotations

import argparse
import json
import subprocess
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1080, 1920
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def fonte(texto, tamanho, largura):
    for n in range(tamanho, 27, -2):
        f = ImageFont.truetype(FONT, n)
        if f.getlength(texto) <= largura:
            return f
    raise ValueError("Texto longo demais para a capa")


def desenhar(frame, meta):
    periodo = meta["periodo"]
    if periodo not in ("manha", "noite"):
        raise ValueError("Turno inválido")
    ref = str(meta["referencia"]).strip()
    if not ref:
        raise ValueError("Referência bíblica ausente")
    manha = periodo == "manha"
    fundo = "#123E40" if manha else "#29234F"
    destaque = "#FFE09A" if manha else "#E3CFFF"
    tipo = "EVANGELHO DO DIA" if manha else "SALMO DA NOITE"

    img = ImageOps.fit(frame.convert("RGB"), (W, H))
    d = ImageDraw.Draw(img)
    # Texto dentro do recorte central quadrado e 3:4 da grade.
    d.rounded_rectangle((70, 440, 1010, 790), radius=42, fill=fundo, outline=destaque, width=5)
    d.text((540, 503), tipo, font=fonte(tipo, 52, 850), fill=destaque, anchor="mm")
    d.line((185, 553, 895, 553), fill=destaque, width=3)
    d.text((540, 625), ref, font=fonte(ref, 100, 860), fill="white", anchor="mm")
    dia = f"DIA {meta['dia']}  |  BÍBLIA EXPLICADA"
    d.text((540, 738), dia, font=fonte(dia, 35, 850), fill=destaque, anchor="mm")
    return img


def gerar(video, ficha, destino):
    meta = json.loads(Path(ficha).read_text(encoding="utf-8"))
    raw = subprocess.check_output([
        "ffmpeg", "-v", "error", "-ss", "0.4", "-i", str(video),
        "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"
    ])
    with Image.open(BytesIO(raw)) as frame:
        img = desenhar(frame, meta)
    img.save(destino, "JPEG", quality=92, optimize=True)
    with Image.open(destino) as capa:
        if capa.size != (W, H) or capa.format != "JPEG":
            raise ValueError("Capa fora do padrão 1080x1920 JPEG")
    print(f"Capa gerada: {destino} ({meta['referencia']})")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video")
    p.add_argument("ficha")
    p.add_argument("destino")
    a = p.parse_args()
    gerar(a.video, a.ficha, a.destino)
