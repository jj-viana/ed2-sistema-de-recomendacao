from src.carregador import carregar_json, buscar_nome_por_id
from src.grafo import (
    grafoLista,
    construir_grafo_bipartido,
    construir_projecao_jogo_jogo
)
from src.recomendador import selecionar_top_jogos
from src.nlp import processar_texto_spacy


def teste_carregamento():
    print("\n=== TESTE 1: CARREGAMENTO DOS JSON ===")

    usuarios = carregar_json("data/usuarios.json")
    jogos = carregar_json("data/jogos.json")
    interacoes = carregar_json("data/interacoes.json")

    assert len(usuarios) == 30
    assert len(jogos) == 40
    assert len(interacoes) > 0

    print("✓ Usuários carregados:", len(usuarios))
    print("✓ Jogos carregados:", len(jogos))
    print("✓ Interações carregadas:", len(interacoes))


def teste_busca_nome():
    print("\n=== TESTE 2: BUSCA POR ID ===")

    jogos = carregar_json("data/jogos.json")

    assert buscar_nome_por_id(jogos, 1) == "Reinos de Eldoria"
    assert buscar_nome_por_id(jogos, 32) == "Refúgio Zumbi"
    assert buscar_nome_por_id(jogos, 40) == "Fronteira Estelar"

    print("✓ Busca por ID funcionando")


def teste_grafo_lista():
    print("\n=== TESTE 3: GRAFO LISTA ===")

    g = grafoLista(4)

    g.adicionar_aresta(0, 1)
    g.adicionar_aresta(0, 2)
    g.adicionar_aresta(1, 3)

    assert g.existe_aresta(0, 1)
    assert g.existe_aresta(0, 2)
    assert g.existe_aresta(1, 3)

    print("Adjacências:")
    print(g.adjacencias)

    print("✓ Grafo lista funcionando")


def teste_grafo_bipartido():
    print("\n=== TESTE 4: GRAFO BIPARTIDO ===")

    usuarios = carregar_json("data/usuarios.json")
    jogos = carregar_json("data/jogos.json")
    interacoes = carregar_json("data/interacoes.json")

    grafo = construir_grafo_bipartido(
        usuarios,
        jogos,
        interacoes
    )

    assert len(grafo.usuarios) == 30
    assert len(grafo.jogos) == 40

    print("Jogos da Ana (id=1):")
    print(grafo.usuarios[0])

    print()

    print("Usuários que jogam Refúgio Zumbi (id=32):")
    print(grafo.jogos[31])

    print("✓ Grafo bipartido funcionando")


def teste_spacy():
    print("\n=== TESTE 5: PROCESSAMENTO spaCy ===")

    texto = """
    RPG de mundo aberto em fantasia medieval
    com exploração, magia antiga e dragões.
    """

    resultado = processar_texto_spacy(texto)

    assert len(resultado) > 0

    print("Palavras encontradas:")
    print(resultado)

    print("✓ spaCy funcionando")


def teste_processar_todos_jogos():
    print("\n=== TESTE 6: PROCESSAR TODOS OS JOGOS ===")

    jogos = carregar_json("data/jogos.json")

    for jogo in jogos:
        palavras = processar_texto_spacy(
            jogo["descricao"]
        )

        assert len(palavras) > 0

    print(f"✓ {len(jogos)} jogos processados com sucesso")


def teste_projecao_jogo_jogo():
    print("\n=== TESTE 7: PROJEÇÃO JOGO-JOGO ===")

    usuarios = carregar_json("data/usuarios.json")
    jogos = carregar_json("data/jogos.json")
    interacoes = carregar_json("data/interacoes.json")

    grafo_bip = construir_grafo_bipartido(
        usuarios,
        jogos,
        interacoes
    )

    palavras_por_jogo = []

    for jogo in jogos:
        palavras_por_jogo.append(
            processar_texto_spacy(
                jogo["descricao"]
            )
        )

    projecao = construir_projecao_jogo_jogo(
        grafo_bip,
        palavras_por_jogo
    )

    assert projecao.quantidade_vertices == 40

    print("Vizinhos dos primeiros jogos:")

    for i in range(5):
        print(
            f"{jogos[i]['nome']} -> "
            f"{projecao.vizinhos(i)}"
        )

    print("✓ Projeção construída com sucesso")


def teste_heap():
    print("\n=== TESTE 8: HEAP DE PRIORIDADE ===")

    scores = [
        (15, "Refúgio Zumbi"),
        (8, "Arena dos Campeões"),
        (25, "Fronteira Estelar"),
        (10, "Festival dos Bichos"),
    ]

    resultado = selecionar_top_jogos(
        scores,
        3
    )

    assert resultado[0][0] == 25
    assert resultado[1][0] == 15
    assert resultado[2][0] == 10

    print("Top recomendações:")
    print(resultado)

    print("✓ Heap funcionando")


def teste_arquivo_inexistente():
    print("\n=== TESTE 9: TRATAMENTO DE ERRO ===")

    try:
        carregar_json("arquivo_que_nao_existe.json")
    except FileNotFoundError:
        print("✓ FileNotFoundError capturado corretamente")
        return

    raise AssertionError(
        "Era esperado FileNotFoundError"
    )


def teste_vertice_invalido():
    print("\n=== TESTE 10: VÉRTICE INVÁLIDO ===")

    g = grafoLista(5)

    try:
        g.adicionar_aresta(0, 10)
    except IndexError:
        print("✓ IndexError capturado corretamente")
        return

    raise AssertionError(
        "Era esperado IndexError"
    )


if __name__ == "__main__":

    print("=" * 50)
    print("INICIANDO TESTES DO PROJETO")
    print("=" * 50)

    teste_carregamento()
    teste_busca_nome()
    teste_grafo_lista()
    teste_grafo_bipartido()
    teste_spacy()
    teste_processar_todos_jogos()
    teste_projecao_jogo_jogo()
    teste_heap()
    teste_arquivo_inexistente()
    teste_vertice_invalido()

    print("\n" + "=" * 50)
    print("TODOS OS TESTES PASSARAM!")
    print("=" * 50)