"""Ponto de entrada do Sistema de Recomendação de Jogos.

Etapas comuns aos dois modos:
  1. carrega os dados (jogos, usuários, interações);
  2. constrói o grafo bipartido Usuário-Jogo (sem peso);
  3. pré-processa as descrições com spaCy (palavras-chave por jogo).

Modo USUÁRIO EXISTENTE (item-item, via projeção Jogo-Jogo):
    python main.py            # usuário de exemplo (id 1)
    python main.py 7          # recomenda para o usuário de id 7
    python main.py 7 10       # 10 recomendações para o usuário de id 7

Modo USUÁRIO NOVO (cold start, similaridade por TEXTO - Q6):
    python main.py --novo "gosto de rpg de fantasia com mundo aberto"
    python main.py --novo "fps multiplayer competitivo" 10
"""

import sys

from src.carregador import carregar_json, buscar_nome_por_id
from src.grafo import construir_grafo_bipartido, construir_projecao_jogo_jogo
from src.nlp import processar_jogos, palavras_chave
from src.recomendador import recomendar, recomendar_usuario_novo

CAMINHO_JOGOS = "data/jogos.json"
CAMINHO_USUARIOS = "data/usuarios.json"
CAMINHO_INTERACOES = "data/interacoes.json"


def nome_do_jogo(jogos, jogo_indice):
    # converte o índice interno do grafo (0-based) no nome do jogo (id = índice + 1)
    return buscar_nome_por_id(jogos, jogo_indice + 1)


def preparar(jogos, usuarios, interacoes):
    # etapas comuns: grafo bipartido + pré-processamento spaCy das descrições
    print("Construindo grafo bipartido Usuário-Jogo...")
    grafo_bipartido = construir_grafo_bipartido(usuarios, jogos, interacoes)
    print("Processando descrições com spaCy (lematização)...")
    palavras_por_jogo = processar_jogos(jogos)
    return grafo_bipartido, palavras_por_jogo


def fluxo_usuario_existente(jogos, usuarios, grafo_bipartido, palavras_por_jogo,
                            usuario_id, quantidade):
    print("Construindo projeção Jogo-Jogo...")
    projecao = construir_projecao_jogo_jogo(grafo_bipartido, palavras_por_jogo)

    usuario_indice = usuario_id - 1
    print("\n" + "=" * 50)
    print(f"Usuário: {buscar_nome_por_id(usuarios, usuario_id)} (id {usuario_id})")

    jogos_consumidos = grafo_bipartido.usuarios[usuario_indice]
    print("Jogos com que já interagiu:")
    if jogos_consumidos:
        for jogo_indice in jogos_consumidos:
            print(f"  - {nome_do_jogo(jogos, jogo_indice)}")
    else:
        print("  (nenhum)")

    recomendacoes = recomendar(usuario_indice, grafo_bipartido, projecao, quantidade)
    print(f"\nTop {quantidade} jogos recomendados:")
    if recomendacoes:
        for posicao, (score, jogo_indice) in enumerate(recomendacoes, start=1):
            print(f"  {posicao}. {nome_do_jogo(jogos, jogo_indice)}  (relevância: {score})")
    else:
        print("  (sem recomendações — usuário sem interações)")
    print("=" * 50)


def fluxo_usuario_novo(jogos, usuarios, grafo_bipartido, palavras_por_jogo,
                       texto, quantidade):
    print("\n" + "=" * 50)
    print("Usuário NOVO (cold start) — similaridade por texto")
    print(f'Texto informado: "{texto}"')

    # texto -> conjunto de palavras-chave (camada de PLN); a recomendação
    # recebe o conjunto já pronto, sem depender do spaCy
    perfil_novo = palavras_chave(texto)
    resultado = recomendar_usuario_novo(
        perfil_novo, grafo_bipartido, palavras_por_jogo, quantidade
    )

    if resultado is None:
        print("\nNão foi possível encontrar um usuário parecido")
        print("(o texto não compartilhou nenhuma palavra-chave com a base).")
        print("=" * 50)
        return

    print(f"Palavras-chave extraídas: {sorted(perfil_novo)}")

    recomendacoes = resultado["recomendacoes"]
    print(f"\nTop {quantidade} jogos recomendados (com o usuário de origem):")
    for posicao, (jogo_indice, usuario_indice, score) in enumerate(recomendacoes, start=1):
        nome_origem = buscar_nome_por_id(usuarios, usuario_indice + 1)
        print(
            f"  {posicao}. {nome_do_jogo(jogos, jogo_indice)}  "
            f"— de {nome_origem} (Jaccard {score:.3f})"
        )

    # lista os usuários parecidos de onde as recomendações vieram (sem repetir)
    usuarios_usados = []
    for _jogo_indice, usuario_indice, score in recomendacoes:
        if (usuario_indice, score) not in usuarios_usados:
            usuarios_usados.append((usuario_indice, score))
    print(f"\nUsuários parecidos usados ({len(usuarios_usados)}):")
    for usuario_indice, score in usuarios_usados:
        nome_usado = buscar_nome_por_id(usuarios, usuario_indice + 1)
        print(f"  - {nome_usado} (id {usuario_indice + 1}) — Jaccard {score:.3f}")
    print("=" * 50)


def main():
    print("Carregando dados...")
    jogos = carregar_json(CAMINHO_JOGOS)
    usuarios = carregar_json(CAMINHO_USUARIOS)
    interacoes = carregar_json(CAMINHO_INTERACOES)
    print(f"  {len(jogos)} jogos | {len(usuarios)} usuários | {len(interacoes)} interações")

    grafo_bipartido, palavras_por_jogo = preparar(jogos, usuarios, interacoes)

    if len(sys.argv) > 1 and sys.argv[1] == "--novo":
        texto = sys.argv[2] if len(sys.argv) > 2 else ""
        quantidade = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        fluxo_usuario_novo(jogos, usuarios, grafo_bipartido, palavras_por_jogo,
                           texto, quantidade)
    else:
        usuario_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
        quantidade = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        fluxo_usuario_existente(jogos, usuarios, grafo_bipartido, palavras_por_jogo,
                                usuario_id, quantidade)


if __name__ == "__main__":
    main()
