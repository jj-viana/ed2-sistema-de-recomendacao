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


def usuario_mais_similar(perfil_novo, perfis):
    # retorna (índice do usuário mais parecido, similaridade de Jaccard).
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


def recomendar_usuario_novo(perfil_novo, grafo_bipartido, palavras_por_jogo, quantidade=5):
    # recebe o conjunto de palavras-chave do usuário novo (já extraído do texto),
    # acha o usuário mais parecido por Jaccard e recomenda os jogos dele.
    # retorna None se nenhum usuário compartilhar qualquer palavra-chave (cold start).
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
        "usuario_similar_indice": indice_similar,
        "similaridade": similaridade,
        "jogos_indices": jogos_ordenados[:quantidade],
    }
