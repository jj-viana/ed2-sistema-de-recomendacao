#lógica de recomendação usando heap de prioridade

from src.grafo import construir_perfis_usuarios


class MaxHeap:

    def __init__(self):
        # começa com um valor falso na posição 0 para não usar ela
        self.dados = [None]

    def tamanho(self):
        # o tamanho real é o comprimento da lista menos o elemento falso do índice 0
        return len(self.dados) - 1

    def esta_vazio(self):
        return self.tamanho() == 0


    def posicao_do_pai(self, i):
        return i // 2

    def posicao_filho_esquerdo(self, i):
        return i * 2

    def posicao_filho_direito(self, i):
        return i * 2 + 1

    def trocar(self, i, j):

        temporario = self.dados[i]
        self.dados[i] = self.dados[j]
        self.dados[j] = temporario

    def pegar_score(self, i):
        return self.dados[i][0]

    def subir(self, i):
        while i > 1:
            pai = self.posicao_do_pai(i)

            if self.pegar_score(i) > self.pegar_score(pai):
                self.trocar(i, pai)
                i = pai  
            else:
                break  

    def descer(self, i):
        while True:
            filho_esq = self.posicao_filho_esquerdo(i)
            filho_dir = self.posicao_filho_direito(i)
            maior = i  
       
            if filho_esq <= self.tamanho():
                if self.pegar_score(filho_esq) > self.pegar_score(maior):
                    maior = filho_esq

            if filho_dir <= self.tamanho():
                if self.pegar_score(filho_dir) > self.pegar_score(maior):
                    maior = filho_dir


            if maior == i:
                break

            self.trocar(i, maior)
            i = maior

    def inserir(self, score, nome_do_jogo):
        novo_elemento = [score, nome_do_jogo]
        self.dados.append(novo_elemento)
        self.subir(self.tamanho())

    def remover_maior(self):
        if self.esta_vazio():
            return None

        raiz = self.dados[1]
        ultimo = self.dados.pop() 
        if not self.esta_vazio():
            self.dados[1] = ultimo  
            self.descer(1)         
        return raiz

def selecionar_top_jogos(lista_de_scores, quantidade):   
    heap = MaxHeap()
    for item in lista_de_scores:
        score = item[0]
        nome = item[1]
        heap.inserir(score, nome)

    recomendacoes = []
    for i in range(quantidade):
        resultado = heap.remover_maior()

        if resultado is None:
            break
        recomendacoes.append(resultado)

    return recomendacoes


def recomendar(usuario_indice, grafo_bipartido, projecao, quantidade=5):
    # Etapa D: recomendação item-item a partir da projeção Jogo-Jogo.
    # Retorna uma lista de pares [score, jogo_indice] já ordenada pela heap.
    if usuario_indice < 0 or usuario_indice >= grafo_bipartido.quantidade_usuarios:
        raise IndexError("Usuário inválido na recomendação.")

    # jogos com que o usuário já interagiu (não podem ser recomendados de novo)
    jogos_consumidos = set(grafo_bipartido.usuarios[usuario_indice])

    # conta quantas vezes cada candidato aparece como vizinho, na projeção,
    # dos jogos que o usuário já consumiu
    frequencia_candidatos = {}
    for jogo in jogos_consumidos:
        for vizinho in projecao.vizinhos(jogo):
            if vizinho in jogos_consumidos:
                continue
            frequencia_candidatos[vizinho] = frequencia_candidatos.get(vizinho, 0) + 1

    # monta a lista [score, jogo_indice] e usa a heap para pegar os top-N
    lista_de_scores = [
        [frequencia, jogo_indice]
        for jogo_indice, frequencia in frequencia_candidatos.items()
    ]
    return selecionar_top_jogos(lista_de_scores, quantidade)


# --- Recomendação para usuário NOVO (cold start por texto, Etapa E / Q6) ---
# Um usuário novo chega sem nenhuma aresta no grafo, então a similaridade não
# pode vir de jogos em comum (seria zero): ela vem do TEXTO que ele digita,
# comparado por Jaccard com o perfil de palavras-chave de cada usuário.

def jaccard(conjunto_a, conjunto_b):
    # similaridade de Jaccard: |interseção| / |união|, resultado em [0, 1]
    uniao = len(conjunto_a | conjunto_b)
    if uniao == 0:
        return 0.0
    return len(conjunto_a & conjunto_b) / uniao


def usuarios_similares(perfil_novo, perfis):
    # ordena os usuários por similaridade de Jaccard com o perfil do usuário novo
    # (desempate por maior interseção). Retorna lista de (indice, score) com score > 0.
    ranqueados = []
    for indice, perfil in enumerate(perfis):
        score = jaccard(perfil_novo, perfil)
        if score > 0.0:
            ranqueados.append((indice, score, len(perfil_novo & perfil)))
    ranqueados.sort(key=lambda item: (item[1], item[2]), reverse=True)
    return [(indice, score) for indice, score, _intersecao in ranqueados]


def recomendar_usuario_novo(perfil_novo, grafo_bipartido, palavras_por_jogo, quantidade=5):
    # recebe o conjunto de palavras-chave do usuário novo (já extraído do texto) e
    # recomenda jogos dos usuários mais parecidos por Jaccard, em ordem, até atingir
    # a quantidade pedida. Retorna None se ninguém compartilhar palavra-chave.
    perfis = construir_perfis_usuarios(grafo_bipartido, palavras_por_jogo)
    similares = usuarios_similares(perfil_novo, perfis)
    if not similares:
        return None

    # percorre os usuários do mais parecido ao menos parecido, herdando os jogos
    # deles (ordenados por relevância textual) sem repetir, até completar a lista.
    # O usuário mais parecido tem prioridade; os demais só entram para preencher.
    # Cada recomendação guarda de QUAL usuário (e com que Jaccard) ela veio.
    recomendacoes = []  # (jogo_indice, usuario_indice, similaridade_do_usuario)
    ja_incluidos = set()
    for usuario_indice, score in similares:
        jogos_do_usuario = sorted(
            grafo_bipartido.usuarios[usuario_indice],
            key=lambda jogo_indice: len(
                perfil_novo & {termo for termo, _f in palavras_por_jogo[jogo_indice]}
            ),
            reverse=True,
        )
        for jogo_indice in jogos_do_usuario:
            if jogo_indice not in ja_incluidos:
                ja_incluidos.add(jogo_indice)
                recomendacoes.append((jogo_indice, usuario_indice, score))
        if len(recomendacoes) >= quantidade:
            break

    return {
        "usuario_similar_indice": similares[0][0],
        "similaridade": similares[0][1],
        "recomendacoes": recomendacoes[:quantidade],
    }
