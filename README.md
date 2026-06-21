# Sistema de Recomendação de Jogos

Projeto da disciplina **Estruturas de Dados 2 (FGA0030)** — Tema B: sistema de
recomendação de textos com **grafo bipartido**, **projeção** e
**Processamento de Linguagem Natural (PLN)**.

A área de aplicação escolhida foi **games**: o texto processado por PLN são as
**descrições dos jogos** (gênero, mecânicas, tema). A partir das interações dos
usuários e das palavras-chave das descrições, o sistema recomenda novos jogos.

---

## Como funciona (visão geral)

O sistema tem **dois modos de recomendação**:

1. **Usuário existente** (filtragem item–item): a partir dos jogos que o usuário
   já jogou, busca jogos relacionados na **projeção Jogo–Jogo** e ordena por
   relevância com uma **heap**.
2. **Usuário novo** (cold start por texto — *responde à pergunta Q6 do professor*):
   o usuário digita uma frase descrevendo seus gostos; o sistema compara esse
   texto com o **perfil de palavras-chave** de cada usuário existente
   (**similaridade de Jaccard**), encontra o usuário mais parecido e recomenda os
   jogos dele.

> **Modelagem sem peso:** as arestas do grafo apenas existem ou não existem (não
> guardam nota/tipo). A relevância emerge de **contagens** e de **sobreposição de
> conjuntos**, nunca de pesos.

Para o detalhamento técnico de cada arquivo, algoritmo e complexidade, veja
[`docs/documentacao.md`](docs/documentacao.md).

---

## Estrutura do projeto

```text
ed2-sistema-de-recomendacao/
├── main.py                  # ponto de entrada (CLI) — orquestra os dois modos
├── requirements.txt         # dependências (spaCy)
├── data/                    # dados fictícios em JSON
│   ├── jogos.json           # 40 jogos: { id, nome, genero, descricao }
│   ├── usuarios.json        # 30 usuários: { id, nome }
│   └── interacoes.json      # 168 interações: { user_id, game_id }
├── src/
│   ├── carregador.py        # leitura dos JSON e busca de nome por id
│   ├── nlp.py               # pré-processamento textual com spaCy (lematização)
│   ├── grafo.py             # grafo bipartido + projeção Jogo–Jogo + perfis de usuário
│   └── recomendador.py      # heap + recomendação item–item (Etapa D) e por texto (Etapa E / Q6)
├── tests/
│   └── test_recomendador.py
└── docs/                    # proposta, enunciado e documentação técnica
```

---

## Pré-requisitos

- **Python 3.10+** (testado com 3.12)
- **pip**

---

## Instalação (passo a passo)

```bash
# 1. clonar o repositório
git clone https://github.com/jj-viana/ed2-sistema-de-recomendacao.git
cd ed2-sistema-de-recomendacao

# 2. (recomendado) criar e ativar um ambiente virtual
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. instalar as dependências
pip install -r requirements.txt

# 4. baixar o modelo de português do spaCy (NÃO vem no pip)
python -m spacy download pt_core_news_sm
```

---

## Como rodar

### Modo 1 — Usuário existente (item–item)

```bash
python main.py            # usuário de exemplo (id 1)
python main.py 7          # recomenda para o usuário de id 7
python main.py 7 10       # 10 recomendações para o usuário de id 7
```

### Modo 2 — Usuário novo (texto / cold start)

```bash
python main.py --novo "gosto de rpg de fantasia com mundo aberto"
python main.py --novo "fps multiplayer competitivo" 10
```

---

## Exemplo de saída

**Usuário existente:**

```text
==================================================
Usuário: Ana (id 1)
Jogos com que já interagiu:
  - Refúgio Zumbi
  - Festival dos Bichos
  ...
Top 5 jogos recomendados:
  1. Sombras de Valdaren  (relevância: 5)
  2. Cavaleiro Lunar  (relevância: 5)
  ...
==================================================
```

**Usuário novo:**

```text
==================================================
Usuário NOVO (cold start) — similaridade por texto
Texto informado: "rpg de fantasia com mundo aberto e dragoes"
Palavras-chave extraídas: ['abrir', 'dragoes', 'fantasia', 'mundo', 'rpg']

Top 5 jogos recomendados (com o usuário de origem):
  1. Reinos de Eldoria  — de Sofia (Jaccard 0.056)
  2. Sombras de Valdaren  — de Sofia (Jaccard 0.056)
  3. Dragões do Norte  — de Sofia (Jaccard 0.056)
  ...

Usuários parecidos usados (1):
  - Sofia (id 19) — Jaccard 0.056
==================================================
```

---

## Estruturas de dados e algoritmos (implementados pelo grupo)

| Estrutura / algoritmo | Onde | Papel |
|---|---|---|
| **Grafo bipartido** (lista de adjacência) | `src/grafo.py` | relaciona usuários e jogos (sem peso) |
| **Projeção Jogo–Jogo** | `src/grafo.py` | liga jogos por palavras-chave em comum ou coocorrência de usuários |
| **Recomendação item–item** | `src/recomendador.py` | conta vizinhos na projeção e ordena |
| **Max-heap de prioridade** | `src/recomendador.py` | seleciona os top-N sem ordenar tudo |
| **Perfil de palavras-chave** | `src/grafo.py` | união dos lemas dos jogos de cada usuário |
| **Similaridade de Jaccard** | `src/recomendador.py` | similaridade do usuário novo por texto |

> O spaCy é usado **apenas** para o pré-processamento textual (lematização). Toda
> a modelagem em grafos e a lógica de recomendação são implementadas pelo grupo,
> sem bibliotecas prontas de grafos.

---

## Documentação

- [`docs/documentacao.md`](docs/documentacao.md) — documentação técnica detalhada (arquivo por arquivo, fluxo de dados, algoritmos e complexidade).
- [`docs/proposta/to-do-inicial.md`](docs/proposta/to-do-inicial.md) — proposta do trabalho (respostas às perguntas do professor, incluindo a Q6).
- [`docs/proposta/info-enunciado/`](docs/proposta/info-enunciado/) — enunciado oficial e critérios de avaliação.
