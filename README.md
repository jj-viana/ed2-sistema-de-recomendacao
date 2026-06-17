# Sistema de Recomendação de Jogos

Projeto desenvolvido para a disciplina de Estruturas de Dados 2.

O sistema tem como objetivo recomendar jogos para usuários a partir das interações realizadas e da similaridade textual entre as descrições dos jogos.

## Tema

Sistema de recomendação de textos utilizando:

- Grafo bipartido Usuário–Jogo;
- Projeção Jogo–Jogo;
- Processamento de Linguagem Natural com spaCy;
- Heap de prioridade para seleção das recomendações.

## Área de aplicação

A área escolhida foi games, ou seja, jogos eletrônicos.

As descrições dos jogos são utilizadas como base textual para identificar relações entre jogos com temas, gêneros e mecânicas semelhantes, como mundo aberto, aventura, RPG, FPS, cooperativo, fantasia, entre outros.

## Problema resolvido

O sistema recomenda jogos para um usuário com base nos jogos com os quais ele já interagiu.

A recomendação considera dois fatores principais:

1. Similaridade textual entre descrições de jogos;
2. Relação colaborativa baseada em usuários que interagiram com os mesmos jogos.

## Dados de entrada

Os dados utilizados são fictícios e estão armazenados em arquivos JSON.

Arquivos esperados:

```text
data/jogos.json
data/usuarios.json