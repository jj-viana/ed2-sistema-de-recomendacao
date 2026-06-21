#pré-processamento textual com spaCy
#a saída principal é uma lista de palavras-chave normalizadas por jogo
#a frequência de termos é guardada em uma lista de pares [termo, frequencia]
from __future__ import annotations
from typing import Any
import spacy

# Carregar o modelo português
nlp = spacy.load("pt_core_news_sm")

def processar_texto_spacy(texto: str) -> list[tuple[str, int]]:
    doc = nlp(texto)
    palavras_processadas = []
    for token in doc:
        # descartar stopwords (de, para, com, o, a...), pontuação e não-palavras
        # (números/símbolos). As palavras funcionais já são stopwords, então não
        # precisamos filtrar por classe gramatical — isso evita perder termos de
        # domínio que o etiquetador erra, como a sigla "fps".
        if token.is_stop or token.is_punct or not token.is_alpha:
            continue
        # lematização (normaliza plural/conjugação para a mesma palavra-chave)
        lema = token.lemma_.lower()
        if len(lema) >= 2:
            palavras_processadas.append(lema)

    # Contar a frequência das palavras
    frequencia_palavras = {}

    for palavra in palavras_processadas:
        frequencia_palavras[palavra] = frequencia_palavras.get(palavra,0) + 1
    
    # Retornar (termo, frequencia)
    return sorted(frequencia_palavras.items())


def processar_jogos(jogos: list[dict[str, Any]]) -> list[list[tuple[str, int]]]:
    # processa a descrição de cada jogo e devolve as palavras-chave indexadas
    # por jogo. A posição i da lista corresponde ao jogo de id (i + 1),
    # mesma convenção usada na construção do grafo bipartido (game_id - 1).
    palavras_por_jogo: list[list[tuple[str, int]]] = [[] for _ in range(len(jogos))]
    for jogo in jogos:
        indice = int(jogo["id"]) - 1
        palavras_por_jogo[indice] = processar_texto_spacy(jogo["descricao"])
    return palavras_por_jogo


def palavras_chave(texto: str) -> set[str]:
    # conjunto de lemas (palavras-chave) extraídos de um texto livre.
    # usado para representar a frase digitada por um usuário novo.
    return {termo for termo, _frequencia in processar_texto_spacy(texto)}


#Teste só para ver se está rodando certo
if __name__ == "__main__":
    print("Executando teste do módulo nlp.py...")
    texto_exemplo = "RPG de mundo aberto. Explorar o mundo de RPG é incrível!"
    resultado = processar_texto_spacy(texto_exemplo)
    
    for termo, freq in resultado:
        print(f"Termo: {termo} | Freq: {freq}")