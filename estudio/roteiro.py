"""Roteiro determinístico do canal Lendo a Bíblia Explicada.

O item traz a abertura, os blocos (versículos + comentário em palavras
simples), uma pergunta de fecho e o convite final. Cada versículo vira um
segmento "passagem" e cada comentário um segmento "comentario": é o que
permite o cartão trocar no tempo exato da fala e nunca misturar Escritura
com explicação.
"""
from __future__ import annotations

HANDLE = "@lendoabibliaexplicada"


def convite(item):
    return item.get("convite") or "Siga para ler junto todos os dias."


def blocos(item):
    if item.get("blocos"):
        return item["blocos"]
    return [{"versiculos": item["versiculos"], "comentario": ""}]


def versiculos(item):
    return [v for b in blocos(item) for v in b["versiculos"]]


def comentarios(item):
    return [b["comentario"].strip() for b in blocos(item) if b.get("comentario", "").strip()]


def montar(item: dict) -> list[dict]:
    saida = [dict(papel="abertura", texto=item["abertura"].strip(), expressao="acolhimento", gesto="explicando")]
    for b in blocos(item):
        for v in b["versiculos"]:
            saida.append(dict(papel="passagem", texto=v["texto"].strip(), expressao="reflexao", gesto="livro"))
        if b.get("comentario", "").strip():
            saida.append(dict(papel="comentario", texto=b["comentario"].strip(), expressao="acolhimento",
                              gesto="explicando"))
    if item.get("pergunta"):
        saida.append(dict(papel="pergunta", texto=item["pergunta"].strip(), expressao="duvida", gesto="apontar"))
    saida.append(dict(papel="cta", texto=item["cta"].strip(), expressao="paz", gesto="coracao"))
    for s in saida:
        s["palavras"] = len(s["texto"].split())
    return saida


def texto_falado(item: dict) -> str:
    return " ".join(s["texto"] for s in montar(item))


def palavras_totais(item: dict) -> int:
    return len(texto_falado(item).split())
