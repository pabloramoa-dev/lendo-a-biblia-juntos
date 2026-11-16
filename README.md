# Lendo a Bíblia Explicada

Canal automatizado de leitura diária e comentada da Bíblia: um trecho de um
Evangelho de manhã e um Salmo à noite, explicados em palavras simples.

O motor de vídeo veio do canal Sábio e Feliz (Manim + HyperFrames + voz Kokoro),
com personagem, cenário e roteiro próprios.

## O que tem aqui

| Pasta | Conteúdo |
|---|---|
| `conteudo/plano.json` | O ano inteiro: 730 episódios (365 manhãs e 365 noites), com livro, capítulo e versículos de cada um |
| `conteudo/biblia/` | Texto de Marcos, João e Salmos (Bíblia Livre) |
| `conteudo/comentarios/` | Comentários para os 730 episódios, em 27 lotes. `lote-001.json` cobre os dias 1 a 14; os demais completam os dias 15 a 365 |
| `estudio/` | Motor de vídeo: personagem (`leitor_lib.py`), cena, voz e composição |
| `tools/` | `planejar` (gera o plano), `montar_item` (monta um episódio), `piloto` (renderiza um episódio) |

## Plano do primeiro ano

- **Manhã:** Marcos inteiro (169 dias) e depois João, até o capítulo 19.
- **Noite:** Salmos 1 a 116. Salmo curto vai inteiro; salmo longo é dividido.
- Cada episódio lê de 3 a 7 versículos, em blocos, com um comentário curto depois de cada bloco.

Todos os 730 episódios do plano têm comentário escrito, ligado ao trecho bíblico e com explicação ou aplicação para o dia a dia. O montador ainda permite leitura pura como alternativa para um episódio novo que não tenha comentário cadastrado.

## Como renderizar um episódio

```
pip install -r requirements.txt -r requirements-estudio.txt
npm ci --prefix video
python -m tools.piloto M001
```

## O que ainda falta

- Cenário da noite para os Salmos (hoje a noite usa o mesmo cenário da manhã).
- Capa central com "Dia N · referência" para a grade do Instagram.
- Conectar e adaptar a publicação no Instagram para @lendoabibliaexplicada (a rotina atual produz e entrega os vídeos).
- Trocar a voz, se uma das vozes neurais em teste for aprovada.

## Texto bíblico

Bíblia Livre (BLIVRE), versão Textus Receptus — https://github.com/blivre/BibliaLivre —
licença Creative Commons Atribuição 3.0 Brasil. A marca musical "(Selá)" e os
títulos dos Salmos não são lidos. Os comentários são do canal e aparecem sempre
em cartão separado do texto bíblico.

## Produção automática — 6h e 18h (Brasília)

O workflow `Produzir episódios bíblicos`, em `.github/workflows/producao_diaria.yml`,
inicia a produção todos os dias às **6h** (Evangelhos) e **18h** (Salmos).
São 09h e 21h em UTC. O horário é de início; o MP4 fica pronto após a renderização.
O agendador do GitHub pode começar com atraso.

Cada turno escolhe o próximo episódio ainda não produzido de seu período. Se um
dia falhar, a próxima execução retoma esse episódio, sem pular para o seguinte.
Uma execução repetida no mesmo turno e data não produz outro vídeo. O histórico
fica em `conteudo/produzidos.json` e só avança depois da validação e do upload.
Ao terminar os 365 episódios de um período, a rotina para sem reciclar conteúdo.

A entrega aparece em **Actions → execução → Artifacts**, com MP4 1080×1920,
`legenda.txt` e `episodio.json` (voz, duração, referência e hash do vídeo).
Os arquivos ficam disponíveis por **7 dias**; o histórico continua no repositório.
O processamento usa o mesmo Leitor, cenário, Kokoro e HyperFrames do piloto.
A voz é `pm_alex+im_nicola`, em velocidade 0,94, com leitura e comentário separados.
Modelos Kokoro ficam em cache entre execuções. Não há chamada a API paga de voz.

Para executar manualmente: **Actions → Produzir episódios bíblicos → Run workflow**.
Escolha `rotina` e o período para produzir o próximo; escolha `piloto` e um ID
como `M001` ou `N001` para gerar uma prévia sem consumir a sequência diária.
Um push que altera a rotina gera automaticamente um piloto `N001` como teste
completo, também sem avançar o histórico.

A rotina atual não chama o publicador do Instagram herdado do Sábio e Feliz.
A conexão e a conferência de @lendoabibliaexplicada são uma etapa separada.

Verificação local da seleção e dos 730 comentários:

```bash
python -m unittest discover -s tests -p test_rotina.py -v
```
