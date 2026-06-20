#lógica de recomendação usando heap de prioridade


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
