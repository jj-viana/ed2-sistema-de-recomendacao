from __future__ import annotations
import json
from pathlib import Path
from typing import Any


def carregar_json(caminho: str | Path) -> list[dict[str, Any]]:#carregar arquivos JSON
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    with caminho.open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, list):
        raise ValueError(f"O arquivo {caminho} deve conter uma lista JSON.")
    return dados

def buscar_nome_por_id(registros: list[dict[str, Any]], identificador: int) -> str:#busca um usuário ou jogo a partir do seu ID
    for registro in registros:
        if int(registro["id"]) == identificador:
            return str(registro["nome"])
    return "Registro não encontrado"
