# Lendo a Bíblia Explicada

**Instagram oficial:** [@lendoabibliaexplicada](https://www.instagram.com/lendoabibliaexplicada/).

Canal automatizado de leitura diária e comentada da Bíblia: um trecho de um
Evangelho de manhã e um Salmo à noite, explicados em palavras simples.

O motor de vídeo veio do canal Sábio e Feliz (Manim + HyperFrames + voz Kokoro),
com personagem, cenário e roteiro próprios.

## Identidade e conexão com o Instagram

- **Nome do canal:** Lendo a Bíblia Explicada.
- **Usuário oficial:** `@lendoabibliaexplicada`.
- **Trava de segurança:** os publicadores conferem o `username` retornado pela Meta e recusam publicar em outra conta.
- **Secrets necessários na futura configuração:** `IG_USER_ID_BIBLIA` e `IG_ACCESS_TOKEN_BIBLIA`; não reutilize os secrets de outro canal.
- **Endereço público dos arquivos:** configure `RAW_BASE_URL` para o endereço real deste repositório. Ao renomeá-lo no GitHub para `lendo-a-biblia-explicada`, atualize também essa variável.
- **Publicação:** permanece desativada por padrão (`PUBLICAR_ATIVO=false`, `DRY_RUN=true`) até a conexão e validação da conta.

## O que tem aqui

| Pasta | Conteúdo |
|---|---|
| `conteudo/plano.json` | O ano inteiro: 730 episódios (365 manhãs e 365 noites), com livro, capítulo e versículos de cada um |
| `conteudo/biblia/` | Texto de Marcos, João e Salmos (Bíblia Livre) |
| `conteudo/comentarios/` | Comentários por lote. `lote-001.json` cobre os dias 1 a 14 |
| `estudio/` | Motor de vídeo: personagem (`leitor_lib.py`), cena, voz e composição |
| `tools/` | `planejar` (gera o plano), `montar_item` (monta um episódio), `piloto` (renderiza um episódio) |

## Plano do primeiro ano

- **Manhã:** Marcos inteiro (169 dias) e depois João, até o capítulo 19.
- **Noite:** Salmos 1 a 116. Salmo curto vai inteiro; salmo longo é dividido.
- Cada episódio lê de 3 a 7 versículos, em blocos, com um comentário curto depois de cada bloco.

Episódio que ainda não tem comentário escrito sai como leitura pura, então o canal nunca fica sem vídeo.

## Como renderizar um episódio

```
pip install -r requirements.txt -r requirements-estudio.txt
npm ci --prefix video
python -m tools.piloto M001
```

## O que ainda falta

- Escrever os comentários dos dias 15 a 365 (novos arquivos `lote-00X.json`).
- Cenário da noite para os Salmos (hoje a noite usa o mesmo cenário da manhã).
- Capa central com "Dia N · referência" para a grade do Instagram.
- Fila, publicação e workflows do GitHub Actions (entram quando a conta do Instagram for conectada).
- Trocar a voz, se uma das vozes neurais em teste for aprovada.

## Texto bíblico

Bíblia Livre (BLIVRE), versão Textus Receptus — https://github.com/blivre/BibliaLivre —
licença Creative Commons Atribuição 3.0 Brasil. A marca musical "(Selá)" e os
títulos dos Salmos não são lidos. Os comentários são do canal e aparecem sempre
em cartão separado do texto bíblico.
