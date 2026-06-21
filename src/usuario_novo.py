"""Fluxo de recomendação para USUÁRIO NOVO (cold start) a partir de TEXTO.

Resolve a pergunta Q6: "como calcular a similaridade de um usuário novo com os
outros da base?". Um usuário novo chega SEM nenhuma aresta no grafo bipartido,
então a similaridade não pode vir de jogos em comum (seria zero). Ela vem do
TEXTO que ele digita:

  1. cada usuário existente recebe um PERFIL de palavras-chave = união dos lemas
     das descrições dos jogos com que ele interagiu (percorrendo o grafo);
  2. o texto do usuário novo é processado pelo spaCy, virando outro conjunto de
     lemas;
  3. compara-se os dois conjuntos pelo índice de Jaccard (interseção / união);
  4. o usuário existente mais parecido (maior Jaccard) é o "vizinho de gosto";
  5. recomendam-se os jogos desse vizinho ao usuário novo.

O grafo continua sem peso: as arestas só existem ou não existem.
"""

from __future__ import annotations
from typing import Any

from src.nlp import processar_texto_spacy


def construir_perfil_usuario(grafo_bipartido, palavras_por_jogo, usuario_indice) -> set[str]:
    # perfil = união dos lemas das descrições dos jogos do usuário (percorre o grafo)
    perfil: set[str] = set()
    for jogo_indice in grafo_bipartido.usuarios[usuario_indice]:
        for termo, _frequencia in palavras_por_jogo[jogo_indice]:
            perfil.add(termo)
    return perfil


def construir_perfis_usuarios(grafo_bipartido, palavras_por_jogo) -> list[set[str]]:
    # monta o perfil de palavras-chave de todos os usuários da base (uma vez só)
    return [
        construir_perfil_usuario(grafo_bipartido, palavras_por_jogo, usuario_indice)
        for usuario_indice in range(grafo_bipartido.quantidade_usuarios)
    ]


def jaccard(conjunto_a: set[str], conjunto_b: set[str]) -> float:
    # similaridade de Jaccard: |interseção| / |união|, resultado em [0, 1]
    uniao = len(conjunto_a | conjunto_b)
    if uniao == 0:
        return 0.0
    return len(conjunto_a & conjunto_b) / uniao


def usuario_mais_similar(perfil_novo: set[str], perfis: list[set[str]]) -> tuple[int, float]:
    # retorna (índice do usuário existente mais parecido, similaridade de Jaccard).
    # desempate: maior interseção absoluta (quem compartilha mais palavras).
    melhor_indice = -1
    melhor_score = -1.0
    melhor_intersecao = -1
    for indice, perfil in enumerate(perfis):
        score = jaccard(perfil_novo, perfil)
        intersecao = len(perfil_novo & perfil)
        if score > melhor_score or (score == melhor_score and intersecao > melhor_intersecao):
            melhor_indice = indice
            melhor_score = score
            melhor_intersecao = intersecao
    return melhor_indice, melhor_score


def recomendar_para_usuario_novo(
    texto: str,
    grafo_bipartido,
    palavras_por_jogo,
    quantidade: int = 5,
) -> dict[str, Any] | None:
    # processa o texto do usuário novo e recomenda os jogos do usuário mais parecido.
    # retorna None se nenhum usuário compartilhar qualquer palavra-chave (cold start).
    perfil_novo = {termo for termo, _frequencia in processar_texto_spacy(texto)}
    perfis = construir_perfis_usuarios(grafo_bipartido, palavras_por_jogo)

    indice_similar, similaridade = usuario_mais_similar(perfil_novo, perfis)
    if indice_similar < 0 or similaridade <= 0.0:
        return None

    # ordena os jogos do vizinho pela relevância textual com o usuário novo
    # (quantos lemas o jogo compartilha com o texto digitado) e pega os top-N
    jogos_do_vizinho = grafo_bipartido.usuarios[indice_similar]
    jogos_ordenados = sorted(
        jogos_do_vizinho,
        key=lambda jogo_indice: len(
            perfil_novo & {termo for termo, _f in palavras_por_jogo[jogo_indice]}
        ),
        reverse=True,
    )

    return {
        "perfil_novo": perfil_novo,
        "usuario_similar_indice": indice_similar,
        "similaridade": similaridade,
        "jogos_indices": jogos_ordenados[:quantidade],
    }
