# To-Do Inicial — Sistema de Recomendação de Jogos

**Tema sorteado:** B — Sistema de recomendação de textos (grafo bipartido usuário–texto + projeção texto–texto + recomendação).
**Linguagem:** Python · **Biblioteca de PLN:** spaCy.

---

## 1) Área de aplicação
**Games (jogos eletrônicos / videogames).**

O conteúdo textual processado por PLN são as **descrições dos jogos** (sinopse, gênero, mecânicas, tema) e, opcionalmente, *reviews*. É um domínio com vocabulário rico ("mundo aberto", "roguelike", "cooperativo", "fantasia medieval"…), gerando boas sobreposições de palavras-chave entre jogos parecidos. Também é distinto de temas comuns (esportes, notícias), reduzindo risco de penalização por similaridade com outros grupos.

## 2) Problema a resolver
**Recomendar jogos para um usuário** a partir das interações dele e da similaridade textual entre jogos.

> Dado um usuário que já interagiu com alguns jogos (jogou / avaliou / curtiu), sugerir N jogos novos relevantes, combinando dois sinais:
> - **(a) conteúdo:** jogos com descrições textualmente parecidas;
> - **(b) colaborativo:** jogos consumidos por usuários de gosto parecido.

## 3) Input (dados de entrada)
**Dados fictícios gerados por LLM** (permitido pelo enunciado; dá controle e coerência). Três arquivos:

| Arquivo | Conteúdo |
|---|---|
| `jogos.json` | ~40 jogos: `{ id, nome, genero, descricao }` — `descricao` é o **texto** processado |
| `usuarios.json` | ~30 usuários: `{ id, nome }` |
| `interacoes.json` | `{ user_id, game_id, tipo, nota }` — `tipo` ∈ {jogou, avaliou, curtiu, compartilhou} |

A LLM gera usuários **coerentes** (um fã de FPS interage com FPS etc.), para que a coocorrência de usuários tenha significado.
*Alternativa real (upgrade opcional):* API RAWG ou descrições da Steam.

## 4) Modelagem do grafo

### Etapa A — Pré-processamento NLP com spaCy
A banca cobra clareza em **como** o texto é processado. Pipeline:

1. `pip install spacy` + `python -m spacy download pt_core_news_sm`
2. Para cada `descricao`: `nlp(texto)` → para cada token: descartar stopword e pontuação; manter POS ∈ {NOUN, PROPN, ADJ, VERB}; usar `token.lemma_.lower()`.
   - A **lematização** normaliza plural→singular e verbo→infinitivo (resolve "sextas"→"sexta", "jogando"→"jogar"), garantindo que a mesma ideia vire a mesma palavra-chave.
3. Resultado: `jogo_id → Counter({ lema: frequência })` (saco de palavras-chave normalizado).

### Etapa B — Grafo bipartido (Usuário–Jogo)
- **Vértices:** Usuários ∪ Jogos.
- **Arestas:** (u, j) se o usuário u interagiu com o jogo j.
- **Peso da aresta:** força da interação (ex.: nota 1–5, ou por tipo: curtiu=1, jogou=2, avaliou=3, compartilhou=4).
- **Representação:** lista de adjacência (dicionário).

### Etapa C — Projeção Jogo–Jogo
Combina os dois sinais:

- **Similaridade semântica (texto):** para jogos que compartilham lemas,
  `peso_sem = Σ min(freq_j1(k), freq_j2(k))` sobre os lemas comuns k.
  Assim, palavras que mais se repetem entre dois jogos pesam mais — o peso emerge naturalmente da sobreposição de palavras-chave (não é necessário Jaccard).
- **Coocorrência de usuários:** `peso_cooc = nº de usuários que interagiram com j1 e j2` (interseção de vizinhos no grafo bipartido).
- **Combinação:** `w(j1, j2) = α · norm(peso_sem) + β · norm(peso_cooc)`.
- **Filtragem:** manter apenas arestas acima de um limiar e/ou top-k vizinhos por jogo (poda do grafo).

### Etapa D — Recomendação
1. Para o usuário u: obter os jogos já consumidos (vizinhos no bipartido).
2. Candidatos = vizinhos desses jogos na projeção Jogo–Jogo, excluindo os já consumidos.
3. `score(candidato) = Σ peso_interação(u, j_i) · w(j_i, candidato)`.
4. Ordenar e retornar os top-N.

## 5) Estrutura de dados adicional (além do grafo)

**Tabela hash / dicionário como Índice Invertido:** `lema → { jogos que contêm o lema }`.

- **Justificativa técnica:** sem ele, calcular a similaridade exigiria comparar todos os pares de jogos — O(n²). Com o índice invertido, só comparamos jogos que **realmente compartilham alguma palavra-chave**, viabilizando a Etapa C com eficiência.
- **Estrutura complementar (opcional):** fila de prioridade (min-heap) para extrair os **top-N** recomendados sem ordenar a lista inteira.

---

## Algoritmos de grafo implementados pelo grupo (sem biblioteca pronta)
Principais algoritmos:

- Representação por **lista de adjacência**.
- **BFS** (conectividade e cálculo de coocorrência de usuários).
- **Construção da projeção bipartida** (Usuário–Jogo → Jogo–Jogo).
- **Algoritmo de recomendação** por pontuação ponderada (Etapa D).

> Bibliotecas de PLN (spaCy) são permitidas para o pré-processamento de texto; os algoritmos de grafo devem ser do grupo.