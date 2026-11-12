"""Converte os arquivos-fonte da Bíblia Livre (github.com/blivre/BibliaLivre,
pasta textos/f4/tr) para o JSON usado pelo canal.

Uso: python -m tools.importar_blivre CAMINHO/textos/f4/tr
"""
import json, re, sys
from pathlib import Path

LIVROS = {"mar": ("Marcos", "marcos"), "joao": ("João", "joao"), "sal": ("Salmos", "salmos")}
FONTE = "Bíblia Livre (BLIVRE), texto Textus Receptus — github.com/blivre/BibliaLivre"
LICENCA = "Creative Commons Atribuição 3.0 Brasil (CC BY 3.0 BR)"


def limpar(t):
    t = re.sub(r"\\(fn|ref|psalm-title)\b.*?\\\*\1", " ", t, flags=re.S)   # notas, referências, títulos
    t = t.replace("(Selá)", " ")                                    # marca musical, não é lida
    t = re.sub(r"\\\*?[\w-]+", " ", t)                              # qualquer marca restante
    t = t.replace("{", "").replace("}", "")
    t = " ".join(t.split())
    t = re.sub(r"\s+([,.;:!?”’])", r"\1", t)
    t = re.sub(r"([“‘])\s+", r"\1", t)
    return t.strip()


def converter(origem: Path, destino: Path):
    for arq, (nome, slug) in LIVROS.items():
        bruto = (origem / f"{arq}.txt").read_text(encoding="utf-8-sig")
        caps = {}
        for m in re.finditer(r"\\v \w+\.(\d+)\.(\d+)\n(.*?)(?=\\v \w+\.\d+\.\d+\n|\Z)", bruto, flags=re.S):
            c, v, txt = m.group(1), m.group(2), limpar(m.group(3))
            if txt:
                caps.setdefault(c, {})[v] = txt
        destino.mkdir(parents=True, exist_ok=True)
        (destino / f"{slug}.json").write_text(json.dumps(
            {"livro": nome, "fonte": FONTE, "licenca": LICENCA, "capitulos": caps},
            ensure_ascii=False, indent=0), encoding="utf-8")
        print(nome, len(caps), "capítulos", sum(len(x) for x in caps.values()), "versículos")


if __name__ == "__main__":
    converter(Path(sys.argv[1]), Path("conteudo/biblia"))
