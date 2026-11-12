"""Monta o item de um episódio a partir do plano, do texto bíblico e dos comentários.

Uso: python -m tools.montar_item M001        (imprime o item)
Episódio ainda sem comentário escrito sai como leitura pura: o canal nunca
fica sem vídeo.
"""
import json, sys
from pathlib import Path

CONT = Path("conteudo")
UNID = ["zero", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze",
        "treze", "catorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
DEZ = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
CEN = ["", "cento", "duzentos", "trezentos"]


def por_extenso(n: int) -> str:
    if n < 20:
        return UNID[n]
    if n < 100:
        d, u = divmod(n, 10)
        return DEZ[d] + (f" e {UNID[u]}" if u else "")
    if n == 100:
        return "cem"
    c, r = divmod(n, 100)
    return CEN[c] + (f" e {por_extenso(r)}" if r else "")


def _json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def plano():
    return {e["id"]: e for e in _json(CONT / "plano.json")}


def comentarios():
    tudo = {}
    for arq in sorted((CONT / "comentarios").glob("lote-*.json")):
        tudo.update(_json(arq))
    return tudo


def montar(ep_id: str) -> dict:
    e = plano()[ep_id]
    biblia = _json(CONT / "biblia" / f"{e['slug']}.json")
    cap = biblia["capitulos"][str(e["capitulo"])]
    versos = [{"n": n, "texto": cap[str(n)]} for n in range(e["v_ini"], e["v_fim"] + 1) if str(n) in cap]
    com = comentarios().get(ep_id, {})
    salmo = e["slug"] == "salmos"
    nome = "Salmo" if salmo else e["livro"]

    blocos, inicio = [], 0
    for b in com.get("blocos", []):
        fim = max(i for i, v in enumerate(versos) if v["n"] <= b["ate"]) + 1
        assert fim > inicio, f"{ep_id}: bloco 'ate {b['ate']}' fora de ordem"
        blocos.append({"versiculos": versos[inicio:fim], "comentario": b["comentario"]})
        inicio = fim
    if inicio < len(versos):
        blocos.append({"versiculos": versos[inicio:], "comentario": ""})

    if salmo:
        abertura = f"Boa noite. Salmo {por_extenso(e['capitulo'])}. Leia comigo."
        cta = "Amanhã à noite, mais um salmo."
    else:
        abertura = f"Dia {por_extenso(e['dia'])}. {e['livro']}, capítulo {por_extenso(e['capitulo'])}. Leia comigo."
        cta = f"Amanhã a gente continua em {e['livro']}."
    return {
        "id": ep_id, "formato": "L", "periodo": e["periodo"], "dia": e["dia"],
        "livro": nome, "capitulo": e["capitulo"],
        "titulo": f"Dia {e['dia']} · {e['ref']}", "referencia_exibida": e["ref"],
        "abertura": com.get("abertura", abertura), "blocos": blocos,
        "pergunta": com.get("pergunta", ""), "cta": com.get("cta", cta),
        "comentado": bool(com), "credito": "Bíblia Livre (BLIVRE)",
    }


if __name__ == "__main__":
    print(json.dumps(montar(sys.argv[1]), ensure_ascii=False, indent=1))
