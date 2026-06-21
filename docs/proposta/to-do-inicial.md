# To-Do Inicial — Sistema de Recomendação de Jogos

**Tema sorteado:** B — Sistema de recomendação de textos (grafo bipartido usuário–texto + projeção texto–texto + recomendação).
**Linguagem:** Python · **Biblioteca de PLN:** spaCy.

---

## 1) Área de aplicação

**Games (jogos eletrônicos / videogames).**

O conteúdo textual processado por PLN são as **descrições dos jogos**: sinopse, gênero, mecânicas, tema e, opcionalmente, *reviews*. É um domínio com vocabulário rico, com termos como “mundo aberto”, “roguelike”, “cooperativo”, “fantasia medieval”, entre outros, gerando boas relações entre jogos parecidos. Também é uma área diferente de temas mais comuns, o que reduz o risco de similaridade com projetos de outros grupos.

---

## 2) Problema a resolver

**Recomendar jogos para um usuário** a partir das interações dele e da relação textual entre os jogos.

> Dado um usuário que já interagiu com alguns jogos, como jogou, avaliou ou curtiu, o sistema deve sugerir N jogos novos que possam ser relevantes para ele.

A recomendação será baseada em dois sinais:

* **Conteúdo textual:** jogos com descrições parecidas, considerando palavras-chave extraídas por PLN;
* **Relação colaborativa:** jogos consumidos por usuários com gostos semelhantes.

---

## 3) Input — dados de entrada

Serão utilizados **dados fictícios gerados por LLM**, o que é permitido pelo enunciado e possibilita maior controle e coerência dos dados.

Três arquivos serão utilizados:

| Arquivo           | Conteúdo                                                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------- |
| `jogos.json`      | 40 jogos: `{ id, nome, genero, descricao }`. A descrição é o texto processado pelo spaCy.                                |
| `usuarios.json`   | 30 usuários: `{ id, nome }`.                                                                                             |
| `interacoes.json` | 168 interações no formato `{ user_id, game_id }`. **Sem peso:** a interação apenas existe, não guarda nota nem tipo.      |

A LLM foi usada para gerar usuários coerentes. Por exemplo, um usuário que gosta de FPS tende a interagir mais com jogos desse gênero. Isso torna as relações entre usuários e jogos mais significativas para o funcionamento do sistema.

> **Decisão de projeto (sem peso):** seguindo a orientação do professor, as interações **não** têm peso (nota/tipo). O grafo registra apenas *se* houve interação, mantendo o modelo simples. Toda a "força" da recomendação emerge de **contagens** (quantos vizinhos em comum) e de **sobreposição de conjuntos** (Jaccard de palavras-chave), nunca de pesos nas arestas.

*Alternativa real, como melhoria opcional:* utilizar descrições de jogos da API RAWG ou da Steam.

---

## 4) Modelagem do grafo

### Etapa A — Pré-processamento NLP com spaCy

A banca deve compreender claramente como o texto será processado. O pipeline será:

1. Instalar o spaCy:

```bash
pip install spacy
python -m spacy download pt_core_news_sm
```

2. Para cada descrição de jogo, aplicar:

```python
nlp(texto)
```

3. Para cada token do texto:

* descartar stopwords;
* descartar pontuação;
* manter apenas classes gramaticais relevantes, como `NOUN`, `PROPN`, `ADJ` e `VERB`;
* aplicar lematização com `token.lemma_.lower()`.

A **lematização** permite normalizar palavras. Por exemplo:

* “jogando” → “jogar”;
* “mundos” → “mundo”;
* “aventuras” → “aventura”.

Isso ajuda o sistema a reconhecer que palavras diferentes podem representar a mesma ideia.

O resultado dessa etapa será uma lista de palavras-chave normalizadas para cada jogo, podendo também conter a frequência de ocorrência de cada termo na descrição.

Exemplo conceitual:

```python
jogo_01 = [
    ("aventura", 2),
    ("mundo", 1),
    ("aberto", 1),
    ("explorar", 1)
]
```

---

### Etapa B — Grafo bipartido Usuário–Jogo

Será construído um **grafo bipartido**, formado por dois conjuntos de vértices:

* **Usuários**;
* **Jogos**.

As arestas conectam usuários aos jogos com os quais eles interagiram.

Exemplo:

```text
Usuário 1 ─── Jogo A
Usuário 1 ─── Jogo B
Usuário 2 ─── Jogo B
Usuário 2 ─── Jogo C
```

Aresta:

```text
(u, j)
```

Existe uma aresta entre o usuário `u` e o jogo `j` quando o usuário interagiu com aquele jogo.

**Importante:** as arestas não terão peso.
O grafo registrará apenas a existência da interação, ou seja, se o usuário interagiu ou não com determinado jogo.

A representação será feita por **lista de adjacência**, utilizando listas de vizinhos.

Exemplo conceitual:

```python
usuarios_para_jogos = [
    [1, 2, 5],
    [2, 3],
    [1, 4]
]
```

Nesse exemplo, cada posição da lista representa um usuário, e os valores internos representam os jogos conectados a ele.

---

### Etapa C — Projeção Jogo–Jogo

A partir do grafo bipartido Usuário–Jogo, será construída uma **projeção Jogo–Jogo**.

Nessa projeção, os vértices serão apenas jogos.

Uma aresta entre dois jogos será criada quando existir alguma relação relevante entre eles.

Essa relação pode ocorrer de duas formas:

1. **Similaridade textual:** os jogos compartilham palavras-chave extraídas das descrições pelo spaCy;
2. **Coocorrência de usuários:** pelo menos um mesmo usuário interagiu com os dois jogos.

Exemplo:

```text
Jogo A ─── Jogo B
```

Isso significa que os jogos possuem alguma relação textual ou colaborativa.

**Importante:** a projeção também não terá pesos nas arestas.
A aresta apenas indica que existe relação entre os dois jogos, sem atribuir valor numérico a essa ligação.

Critério para criar uma aresta:

```text
Criar aresta entre Jogo A e Jogo B se:
- eles compartilharem palavras-chave relevantes; ou
- tiverem usuários em comum.
```

Assim, o grafo Jogo–Jogo representa uma rede de jogos relacionados.

---

### Etapa D — Recomendação

A recomendação será feita a partir dos jogos já consumidos pelo usuário.

Passos:

1. Obter os jogos já consumidos pelo usuário no grafo bipartido.
2. Buscar, na projeção Jogo–Jogo, os vizinhos desses jogos.
3. Remover da lista os jogos que o usuário já consumiu.
4. Contar quantas vezes cada jogo candidato aparece como vizinho dos jogos já consumidos.
5. Usar uma heap para selecionar os melhores candidatos.
6. Retornar os top-N jogos recomendados.

Exemplo:

```text
Usuário consumiu: Jogo A e Jogo B

Na projeção:
Jogo A está ligado a Jogo C e Jogo D
Jogo B está ligado a Jogo C e Jogo E

Candidatos:
Jogo C aparece 2 vezes
Jogo D aparece 1 vez
Jogo E aparece 1 vez
```

Nesse caso, o Jogo C teria prioridade maior na recomendação, pois aparece relacionado a mais jogos já consumidos pelo usuário.

A pontuação utilizada nessa etapa é apenas um valor auxiliar para ordenar os candidatos.
Ela não representa peso nas arestas do grafo.

---

### Etapa E — Recomendação para usuário NOVO (cold start por texto)

> **Responde à pergunta do professor (Q6): "como calcular a similaridade de um usuário novo com os outros da base?"**

A Etapa D só funciona para um usuário que **já interagiu** com jogos. Um usuário **novo** chega **sem nenhuma aresta** no grafo bipartido, então ele não tem jogos em comum com ninguém — a similaridade colaborativa seria sempre zero. Por isso, para o usuário novo, a similaridade vem do **texto** que ele digita.

**Passos:**

1. **Perfil de cada usuário existente** (calculado uma vez): percorre-se o grafo bipartido do usuário até os jogos dele e faz-se a **união** das palavras-chave (lemas) das descrições desses jogos.

   ```text
   perfil(u) = união dos lemas dos jogos com que u interagiu
   ```

2. **Perfil do usuário novo:** ele digita uma frase livre (ex.: *"gosto de RPG de fantasia com mundo aberto"*). O mesmo pipeline spaCy transforma a frase em um conjunto de lemas.

3. **Similaridade de Jaccard** entre o conjunto do usuário novo e o perfil de cada usuário existente:

   ```text
   similaridade(novo, u) = |lemas_em_comum| / |lemas_no_total|
   ```

   O resultado fica entre 0 e 1. Em caso de empate, desempata-se por maior número de lemas em comum (interseção absoluta).

4. **Escolhe-se o usuário mais parecido** (maior Jaccard) — é o "vizinho de gosto".

5. **Recomendam-se os jogos desse vizinho** ao usuário novo (ordenados pela relevância textual com a frase digitada). Em outras palavras, o usuário novo **herda** as arestas-jogo do vizinho mais parecido — e é assim que surge a aresta que liga o usuário novo ao grafo.

**Por que isso respeita as restrições:** o grafo continua **sem peso** (a similaridade é só contagem de conjuntos, vive fora do grafo); a entrada é **texto**; o fluxo é exatamente *usuário novo → usuário existente parecido → jogos dele → recomendação*; e resolve o **cold start** (funciona mesmo sem nenhuma interação prévia).

---

## 5) Estrutura de dados adicional — Heap de Prioridade

Além do grafo, o projeto utilizará uma **heap de prioridade** como segunda estrutura de dados obrigatória.

A heap será usada na etapa de recomendação para selecionar os top-N jogos mais relevantes para o usuário sem precisar ordenar todos os candidatos manualmente.

### Funcionamento da heap

Cada jogo candidato receberá uma pontuação auxiliar baseada na quantidade de vezes que aparece como vizinho dos jogos já consumidos pelo usuário.

Exemplo:

```text
Jogo C → 2 ocorrências
Jogo D → 1 ocorrência
Jogo E → 1 ocorrência
```

Esses candidatos serão inseridos em uma heap.

### Justificativa técnica

A heap é adequada porque permite recuperar os candidatos mais relevantes com eficiência.

Em vez de ordenar toda a lista de candidatos, a heap permite organizar os jogos por prioridade e extrair os top-N recomendados de forma mais eficiente.

Assim, o projeto utiliza:

* **Grafo:** para representar usuários, jogos e relações entre jogos;
* **Heap:** para priorizar e selecionar os jogos recomendados.

---

## Algoritmos de grafo implementados pelo grupo

Os principais algoritmos e procedimentos implementados serão:

* Representação do grafo por **lista de adjacência**;
* Construção do **grafo bipartido Usuário–Jogo**;
* Construção da **projeção Jogo–Jogo**;
* Percurso dos vizinhos na lista de adjacência;
* Busca dos candidatos à recomendação;
* Contagem de frequência dos candidatos;
* **Construção do perfil de palavras-chave** de cada usuário (percurso no grafo bipartido) e **similaridade de Jaccard** para o usuário novo (Etapa E);
* Uso de **heap de prioridade** para selecionar os top-N jogos recomendados.

As bibliotecas de PLN, como o spaCy, serão usadas apenas para o pré-processamento textual.
Os algoritmos de grafo e a lógica de recomendação serão implementados pelo próprio grupo.
