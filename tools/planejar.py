"""Gera conteudo/plano.json: um ano de leituras (manhã: Evangelhos; noite: Salmos).

Manhã: cada Evangelho é dividido pelas suas cenas (perícopes); cena comprida
vira dois ou três episódios, sempre cortando em fim de frase. Noite: salmo
curto vai inteiro, salmo longo é repartido do mesmo jeito.
Determinístico: rodar de novo dá o mesmo plano.
"""
import json, math
from pathlib import Path

BIB = Path("conteudo/biblia")
DIAS = 365
TETO = 95            # palavras de Escritura por episódio (cerca de 40 s de leitura)
INTEIRO = 120        # até aqui a cena ou o salmo cabe num episódio só

# versículo em que cada cena começa, por capítulo
CENAS = {
 "marcos": {1: [1, 9, 14, 21, 29, 35, 40], 2: [1, 13, 18, 23], 3: [1, 7, 13, 20, 31],
            4: [1, 10, 21, 26, 30, 35], 5: [1, 21, 25, 35], 6: [1, 7, 14, 30, 45, 53],
            7: [1, 14, 24, 31], 8: [1, 11, 14, 22, 27, 31, 34], 9: [1, 2, 14, 30, 33, 38, 42],
            10: [1, 13, 17, 23, 32, 35, 46], 11: [1, 12, 15, 20, 27], 12: [1, 13, 18, 28, 35, 38, 41],
            13: [1, 3, 14, 24, 28, 32], 14: [1, 3, 10, 12, 22, 27, 32, 43, 53, 66],
            15: [1, 6, 16, 21, 33, 42], 16: [1, 9, 14, 19]},
 "joao": {1: [1, 6, 14, 19, 29, 35, 43], 2: [1, 13, 23], 3: [1, 16, 22, 31], 4: [1, 16, 27, 39, 43],
          5: [1, 16, 19, 31], 6: [1, 16, 22, 35, 41, 52, 60], 7: [1, 10, 25, 32, 37, 45],
          8: [1, 12, 21, 31, 39, 48], 9: [1, 13, 24, 35], 10: [1, 7, 22, 31], 11: [1, 17, 28, 38, 45],
          12: [1, 9, 12, 20, 27, 37, 44], 13: [1, 12, 21, 31], 14: [1, 8, 15, 25], 15: [1, 9, 18],
          16: [1, 5, 16, 25], 17: [1, 6, 20], 18: [1, 12, 15, 19, 25, 28], 19: [1, 17, 28, 31, 38],
          20: [1, 11, 19, 24], 21: [1, 15, 20]},
}
MANHA = ["marcos", "joao"]


def _pal(vs):
    return sum(len(t.split()) for _, t in vs)


def _fim_de_frase(t):
    return t.rstrip("”’\"' ").endswith((".", "!", "?"))


def repartir(vs):
    """Divide [(n, texto)] em partes equilibradas de até ~TETO palavras."""
    total = _pal(vs)
    if total <= INTEIRO or len(vs) == 1:
        return [vs]
    partes = math.ceil(total / TETO)
    alvo = total / partes
    saida, atual = [], []
    for i, (n, t) in enumerate(vs):
        atual.append((n, t))
        restam = vs[i + 1:]
        if len(saida) == partes - 1 or not restam:
            continue
        p = _pal(atual)
        prox = len(restam[0][1].split())
        passou = p >= alvo * 0.8 and _fim_de_frase(t)
        estoura = p + prox > alvo * 1.25
        if (passou or estoura) and _pal(restam) >= 20:
            saida.append(atual); atual = []
    if atual:
        saida.append(atual)
    return saida


def do_livro(slug):
    b = json.loads((BIB / f"{slug}.json").read_text(encoding="utf-8"))
    for c in sorted(b["capitulos"], key=int):
        vs = [(int(n), t) for n, t in sorted(b["capitulos"][c].items(), key=lambda x: int(x[0]))]
        inicios = CENAS.get(slug, {}).get(int(c), [1])
        cenas = []
        for k, ini in enumerate(inicios):
            fim = inicios[k + 1] - 1 if k + 1 < len(inicios) else vs[-1][0]
            cena = [(n, t) for n, t in vs if ini <= n <= fim]
            if cena:
                cenas.append(cena)
        for cena in cenas:
            for tr in repartir(cena):
                yield dict(livro=b["livro"], slug=slug, capitulo=int(c), v_ini=tr[0][0], v_fim=tr[-1][0])


def ref(e):
    nome = "Salmo" if e["slug"] == "salmos" else e["livro"]
    faixa = f"{e['v_ini']}-{e['v_fim']}" if e["v_ini"] != e["v_fim"] else str(e["v_ini"])
    return f"{nome} {e['capitulo']}:{faixa}"


def main():
    manha = [e for s in MANHA for e in do_livro(s)]
    noite = list(do_livro("salmos"))
    assert len(manha) >= DIAS and len(noite) >= DIAS, (len(manha), len(noite))
    plano = []
    for d in range(DIAS):
        for per, lista, pref in (("manha", manha, "M"), ("noite", noite, "N")):
            e = dict(lista[d]); e.update(id=f"{pref}{d + 1:03d}", dia=d + 1, periodo=per, ref=ref(e))
            plano.append(e)
    Path("conteudo/plano.json").write_text(json.dumps(plano, ensure_ascii=False, indent=0), encoding="utf-8")
    print(len(plano), "episódios | manhã: Marcos", sum(e["slug"] == "marcos" for e in manha[:DIAS]), "dias, depois João até",
          f"{manha[DIAS - 1]['capitulo']}:{manha[DIAS - 1]['v_fim']}", "| noite: até", ref(noite[DIAS - 1]),
          "| sobram", len(manha) - DIAS, "manhãs e", len(noite) - DIAS, "noites para o ano 2")
    return plano


if __name__ == "__main__":
    main()
