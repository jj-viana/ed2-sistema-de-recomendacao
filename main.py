"""Ponto de entrada do Sistema de Recomendação de Jogos.

Orquestra todas as etapas:
  1. carrega os dados (jogos, usuários, interações);
  2. constrói o grafo bipartido Usuário-Jogo (sem peso);
  3. pré-processa as descrições com spaCy (palavras-chave por jogo);
  4. constrói a projeção Jogo-Jogo;
  5. recomenda os top-N jogos para um usuário de exemplo.

Uso:
    python main.py            # usa o usuário de exemplo (id 1)
    python main.py 7          # recomenda para o usuário de id 7
    python main.py 7 10       # recomenda 10 jogos para o usuário de id 7
"""

import sys

from src.carregador import carregar_json, buscar_nome_por_id
from src.grafo import construir_grafo_bipartido, construir_projecao_jogo_jogo
from src.nlp import processar_jogos
from src.recomendador import recomendar

CAMINHO_JOGOS = "data/jogos.json"
CAMINHO_USUARIOS = "data/usuarios.json"
CAMINHO_INTERACOES = "data/interacoes.json"


def nome_do_jogo(jogos, jogo_indice):
    # converte o índice interno do grafo (0-based) no nome do jogo (id = índice + 1)
    return buscar_nome_por_id(jogos, jogo_indice + 1)


def main():
    # 1) escolher o usuário e a quantidade de recomendações (via argumentos)
    usuario_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    quantidade = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    # 2) carregar os dados
    print("Carregando dados...")
    jogos = carregar_json(CAMINHO_JOGOS)
    usuarios = carregar_json(CAMINHO_USUARIOS)
    interacoes = carregar_json(CAMINHO_INTERACOES)
    print(f"  {len(jogos)} jogos | {len(usuarios)} usuários | {len(interacoes)} interações")

    # 3) construir o grafo bipartido Usuário-Jogo
    print("Construindo grafo bipartido Usuário-Jogo...")
    grafo_bipartido = construir_grafo_bipartido(usuarios, jogos, interacoes)

    # 4) pré-processar as descrições com spaCy
    print("Processando descrições com spaCy (lematização)...")
    palavras_por_jogo = processar_jogos(jogos)

    # 5) construir a projeção Jogo-Jogo
    print("Construindo projeção Jogo-Jogo...")
    projecao = construir_projecao_jogo_jogo(grafo_bipartido, palavras_por_jogo)

    # 6) recomendar para o usuário escolhido
    usuario_indice = usuario_id - 1
    nome_usuario = buscar_nome_por_id(usuarios, usuario_id)

    print("\n" + "=" * 50)
    print(f"Usuário: {nome_usuario} (id {usuario_id})")

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


if __name__ == "__main__":
    main()
