#lógica de recomendação usando heap de prioridade
# heap.py
# Implementação do Heap de Máximo para o sistema de recomendação de jogos


# O heap é guardado como uma lista comum do Python
# O índice 0 fica vazio de propósito para deixar a matemática mais fácil:
#   - pai de qualquer posição i   -->  i // 2
#   - filho esquerdo de i         -->  i * 2
#   - filho direito de i          -->  i * 2 + 1

class MaxHeap:

    def __init__(self):
        # começa com um valor falso na posição 0 para não usar ela
        self.dados = [None]

    def tamanho(self):
        # o tamanho real é o comprimento da lista menos o elemento falso do índice 0
        return len(self.dados) - 1

    def esta_vazio(self):
        return self.tamanho() == 0

    # ------------------------------------------------------------------
    # funções auxiliares de navegação
    # ------------------------------------------------------------------

    def posicao_do_pai(self, i):
        return i // 2

    def posicao_filho_esquerdo(self, i):
        return i * 2

    def posicao_filho_direito(self, i):
        return i * 2 + 1

    def trocar(self, i, j):
        # guarda um temporário para não perder os valores na troca
        temporario = self.dados[i]
        self.dados[i] = self.dados[j]
        self.dados[j] = temporario

    def pegar_score(self, i):
        # cada elemento é uma lista [score, nome_do_jogo]
        # essa função só pega o score para facilitar as comparações
        return self.dados[i][0]

    # ------------------------------------------------------------------
    # subir: usado depois de inserir um elemento no final
    # sobe o elemento enquanto ele for maior que o pai dele
    # ------------------------------------------------------------------

    def subir(self, i):
        # continua subindo enquanto não chegar na raiz (posição 1)
        # e enquanto o elemento for maior que o pai
        while i > 1:
            pai = self.posicao_do_pai(i)

            if self.pegar_score(i) > self.pegar_score(pai):
                self.trocar(i, pai)
                i = pai  # continua verificando a partir do pai
            else:
                break  # já está no lugar certo, para

    # ------------------------------------------------------------------
    # descer: usado depois de remover a raiz
    # desce o elemento enquanto algum filho for maior que ele
    # ------------------------------------------------------------------

    def descer(self, i):
        while True:
            filho_esq = self.posicao_filho_esquerdo(i)
            filho_dir = self.posicao_filho_direito(i)
            maior = i  # assume que o atual é o maior por enquanto

            # verifica se o filho esquerdo existe e é maior
            if filho_esq <= self.tamanho():
                if self.pegar_score(filho_esq) > self.pegar_score(maior):
                    maior = filho_esq

            # verifica se o filho direito existe e é maior que o atual maior
            if filho_dir <= self.tamanho():
                if self.pegar_score(filho_dir) > self.pegar_score(maior):
                    maior = filho_dir

            # se o maior não mudou, o elemento já está no lugar certo
            if maior == i:
                break

            # senão, troca com o filho maior e continua descendo
            self.trocar(i, maior)
            i = maior

    # ------------------------------------------------------------------
    # inserir: adiciona um novo jogo com seu score
    # ------------------------------------------------------------------

    def inserir(self, score, nome_do_jogo):
        # cria o elemento como lista [score, nome]
        novo_elemento = [score, nome_do_jogo]

        # coloca no final da lista
        self.dados.append(novo_elemento)

        # sobe até a posição correta
        self.subir(self.tamanho())

    # ------------------------------------------------------------------
    # remover maior: tira e retorna o jogo com maior score (a raiz)
    # ------------------------------------------------------------------

    def remover_maior(self):
        if self.esta_vazio():
            return None

        # guarda a raiz para retornar no final
        raiz = self.dados[1]

        # move o último elemento para a raiz
        ultimo = self.dados.pop()  # remove o último

        if not self.esta_vazio():
            self.dados[1] = ultimo  # coloca ele na raiz
            self.descer(1)          # desce até o lugar certo

        return raiz


# ------------------------------------------------------------------
# função principal: recebe os scores e devolve os top N jogos
# ------------------------------------------------------------------

def selecionar_top_jogos(lista_de_scores, quantidade):
    # lista_de_scores é uma lista de listas: [[score, nome], [score, nome], ...]
    # quantidade é quantas recomendações queremos

    heap = MaxHeap()

    # insere todos os jogos no heap
    for item in lista_de_scores:
        score = item[0]
        nome = item[1]
        heap.inserir(score, nome)

    # vai retirando os maiores um por um
    recomendacoes = []

    for i in range(quantidade):
        resultado = heap.remover_maior()

        if resultado is None:
            break  # heap ficou vazio antes de chegar na quantidade pedida

        recomendacoes.append(resultado)

    return recomendacoes


# ------------------------------------------------------------------
# teste: roda só quando você executa esse arquivo diretamente
# ------------------------------------------------------------------

if __name__ == "__main__":
    print("Testando o heap.py...")
    print()

    # scores fictícios para testar
    scores_de_exemplo = [
        [0.74, "Hollow Knight"],
        [0.91, "Elden Ring"],
        [0.62, "Celeste"],
        [0.88, "Dark Souls"],
        [0.55, "Ori and the Blind Forest"],
        [0.95, "Sekiro"],
    ]

    top_3 = selecionar_top_jogos(scores_de_exemplo, 3)

    print("Top 3 recomendacoes:")
    posicao = 1
    for item in top_3:
        score = item[0]
        nome = item[1]
        print(posicao, "-", nome, "| score:", score)
        posicao = posicao + 1