from __future__ import annotations
from typing import Any

class grafoLista: # grafo por lista de adjacência
    def __init__(self, quantidade_vertices: int): # definir a quantidade de vertices do grafo
        if quantidade_vertices <= 0:
            raise ValueError("A quantidade de vértices deve ser positiva.")
        self.quantidade_vertices = quantidade_vertices
        self.adjacencias: list[list[int]] = []
        for _ in range(quantidade_vertices):
            self.adjacencias.append([])

    def vertice_valido(self, vertice: int) -> bool: # verifica se o vertice é valido
        return 0 <= vertice < self.quantidade_vertices

    def existe_aresta(self, origem: int, destino: int) -> bool: # verifica se existe uma aresta entre dois vertices
        if not self.vertice_valido(origem) or not self.vertice_valido(destino):
            return False
        return destino in self.adjacencias[origem]

    def adicionar_aresta(self, origem: int, destino: int) -> None: # adiciona uma aresta entre dois vertices
        if not self.vertice_valido(origem) or not self.vertice_valido(destino):
            raise IndexError("Vértice inválido ao adicionar aresta.")
        if origem == destino:
            return
        if not self.existe_aresta(origem, destino):
            self.adjacencias[origem].append(destino)
        if not self.existe_aresta(destino, origem):
            self.adjacencias[destino].append(origem)

    def vizinhos(self, vertice: int) -> list[int]: # retorna a lista de vizinhos de um vertice
        if not self.vertice_valido(vertice):
            raise IndexError("Vértice inválido ao buscar vizinhos.")
        return self.adjacencias[vertice]

class grafoBipartido: # grafo bipartido para relacionar usuários e jogos usando lista
    def __init__(self, quantidade_usuarios: int, quantidade_jogos: int):
        self.quantidade_usuarios = quantidade_usuarios
        self.quantidade_jogos = quantidade_jogos
        self.usuarios: list[list[int]] = ([]) # usuarios[u] contém os jogos conectados ao usuário u
        self.jogos: list[list[int]] = ([]) # jogos[j] contém os usuários conectados ao jogo j
        for _ in range(quantidade_usuarios):
            self.usuarios.append([])
        for _ in range(quantidade_jogos):
            self.jogos.append([])

    def adicionar_interacao(self, usuario_indice: int, jogo_indice: int) -> None: # cria uma aresta entre usuário e jogo
        if usuario_indice < 0 or usuario_indice >= self.quantidade_usuarios:
            raise IndexError("Usuário inválido.")
        if jogo_indice < 0 or jogo_indice >= self.quantidade_jogos:
            raise IndexError("Jogo inválido.")
        if jogo_indice not in self.usuarios[usuario_indice]:
            self.usuarios[usuario_indice].append(jogo_indice)
        if usuario_indice not in self.jogos[jogo_indice]:
            self.jogos[jogo_indice].append(usuario_indice)

def construir_grafo_bipartido(
    usuarios: list[dict[str, Any]],
    jogos: list[dict[str, Any]],
    interacoes: list[dict[str, Any]],
) -> grafoBipartido: # constrói o grafo bipartido Usuário-Jogo.
    grafo = grafoBipartido(len(usuarios), len(jogos))
    for interacao in interacoes:
        usuario_indice = int(interacao["user_id"]) - 1
        jogo_indice = int(interacao["game_id"]) - 1
        grafo.adicionar_interacao(usuario_indice, jogo_indice)
    return grafo

def contar_palavras_comuns(
    palavras_jogo_a: list[list[Any]],
    palavras_jogo_b: list[list[Any]],
) -> int: # conta quantas palavras-chave aparecem nos dois jogos
    quantidade = 0
    for termo_a in palavras_jogo_a:
        for termo_b in palavras_jogo_b:
            if termo_a[0] == termo_b[0]:
                quantidade += 1
                break
    return quantidade

def construir_projecao_jogo_jogo(
    grafo_bipartido: grafoBipartido,
    palavras_por_jogo: list[list[list[Any]]],
    minimo_palavras_comuns: int = 2,
) -> grafoLista: # constrói a projeção Jogo-Jogo sem pesos nas arestas
    quantidade_jogos = grafo_bipartido.quantidade_jogos
    projecao = grafoLista(quantidade_jogos)

    # critério 1: similaridade textual por compartilhamento de palavras-chave
    for jogo_a in range(quantidade_jogos):
        for jogo_b in range(jogo_a + 1, quantidade_jogos):
            comuns = contar_palavras_comuns(
                palavras_por_jogo[jogo_a],
                palavras_por_jogo[jogo_b],
            )
            if comuns >= minimo_palavras_comuns:
                projecao.adicionar_aresta(jogo_a, jogo_b)

    # critério 2: coocorrência de usuários
    # se um mesmo usuário interagiu com dois jogos, esses jogos ficam ligados
    for jogos_do_usuario in grafo_bipartido.usuarios:
        for posicao_a in range(len(jogos_do_usuario)):
            for posicao_b in range(posicao_a + 1, len(jogos_do_usuario)):
                jogo_a = jogos_do_usuario[posicao_a]
                jogo_b = jogos_do_usuario[posicao_b]
                projecao.adicionar_aresta(jogo_a, jogo_b)
    return projecao