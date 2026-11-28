"""Gera uma capa exclusiva para a grade do Instagram, sem alterar o MP4.

Uso: python -m tools.capa_biblia midia/M001.mp4 midia/episodio.json midia/M001.jpg
"""
from __future__ import annotations

import argparse
import json
import re
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


def textos_editoriais(meta):
    # O título e a reflexão vêm do roteiro real, não de texto gerado ao acaso.
    from tools.montar_item import comentarios
    com = comentarios().get(meta["id"], {})
    abertura = " ".join(com.get("abertura", "").split())
    titulo = re.sub(r"^(?:Dia [^.?!]+[.!]|Boa noite[.!]|Bom dia[.!])\s*", "", abertura, flags=re.I)
    titulo = re.sub(r"\s*Leia comigo[.!?]?\s*$", "", titulo, flags=re.I).strip(" .")
    pergunta = " ".join(com.get("pergunta", "").split())
    if not titulo or re.fullmatch(r"(?:Salmo|Marcos|Mateus|Lucas|João)[\w\s,:-]*", titulo, flags=re.I) and len(titulo.split()) <= 3:
        titulo = pergunta or "Leitura e explicação em palavras simples"
    return titulo, pergunta if pergunta != titulo else ""


def linhas(texto, font, largura):
    resultado, atual = [], ""
    for palavra in texto.split():
        candidato = (atual + " " + palavra).strip()
        if font.getlength(candidato) <= largura:
            atual = candidato
        else:
            if atual:
                resultado.append(atual)
            atual = palavra
    if atual:
        resultado.append(atual)
    return resultado


def bloco(d, texto, centro_y, largura, max_linhas, tamanho, minimo, cor):
    for n in range(tamanho, minimo - 1, -2):
        f = ImageFont.truetype(FONT, n)
        ls = linhas(texto, f, largura)
        if len(ls) <= max_linhas and all(f.getlength(l) <= largura for l in ls):
            break
    else:
        f = ImageFont.truetype(FONT, minimo)
        ls = linhas(texto, f, largura)[:max_linhas]
        if ls:
            ultima = ls[-1]
            while ultima and f.getlength(ultima + "…") > largura:
                ultima = ultima[:-1]
            ls[-1] = ultima.rstrip() + "…"
    passo = f.size * 1.16
    for i, l in enumerate(ls):
        d.text((540, centro_y + (i - (len(ls) - 1) / 2) * passo), l,
               font=f, fill=cor, anchor="mm")


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
    tipo = "EVANGELHO DO DIA • 6H" if manha else "SALMO DA NOITE • 21H"
    titulo, pergunta = textos_editoriais(meta)

    img = ImageOps.fit(frame.convert("RGB"), (W, H))
    d = ImageDraw.Draw(img)
    # Painéis dentro do recorte central; mantém o rosto visível entre os dois.
    d.rounded_rectangle((70, 440, 1010, 830), radius=42, fill=fundo, outline=destaque, width=5)
    d.text((540, 492), tipo, font=fonte(tipo, 42, 850), fill=destaque, anchor="mm")
    d.line((185, 533, 895, 533), fill=destaque, width=3)
    bloco(d, titulo, 646, 850, 3, 70, 42, "white")
    d.text((540, 785), ref, font=fonte(ref, 56, 860), fill=destaque, anchor="mm")

    d.rounded_rectangle((70, 1260, 1010, 1475), radius=34, fill=fundo, outline=destaque, width=4)
    if pergunta:
        d.text((540, 1295), "REFLEXÃO PARA HOJE", font=fonte("REFLEXÃO PARA HOJE", 32, 850),
               fill=destaque, anchor="mm")
        bloco(d, pergunta, 1370, 850, 3, 44, 30, "white")
    else:
        bloco(d, "Entenda a Palavra de Deus e leve para a sua vida", 1355, 850, 2, 44, 34, "white")
    rodape = f"DIA {meta['dia']}  •  BÍBLIA EXPLICADA"
    d.text((540, 1448), rodape, font=fonte(rodape, 30, 850), fill=destaque, anchor="mm")
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
