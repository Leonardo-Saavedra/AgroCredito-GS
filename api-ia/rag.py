import numpy as np
from google import genai

import config
from documentos import DOCUMENTOS

client = genai.Client(api_key=config.GEMINI_API_KEY)

_indice = None


def _normalizar(vetor) -> np.ndarray:
    v = np.array(vetor, dtype=float)
    return v / np.linalg.norm(v)


def gerar_embeddings(textos: list) -> list:
    resposta = client.models.embed_content(
        model=config.EMBEDDING_MODEL,
        contents=textos,
    )
    return [_normalizar(e.values) for e in resposta.embeddings]


def indexar_documentos() -> list:
    global _indice
    if _indice is None:
        textos = [f"{doc['titulo']}. {doc['conteudo']}" for doc in DOCUMENTOS]
        vetores = gerar_embeddings(textos)
        _indice = list(zip(DOCUMENTOS, vetores))
    return _indice


def buscar_documentos(pergunta: str, top_k: int | None = None, score_minimo: float | None = None) -> list:
    top_k = top_k or config.RAG_TOP_K
    minimo = config.RAG_SCORE_MINIMO if score_minimo is None else score_minimo

    indice = indexar_documentos()
    consulta = gerar_embeddings([pergunta])[0]

    pontuados = []
    for doc, vetor in indice:
        score = float(np.dot(consulta, vetor))
        pontuados.append({**doc, "score": round(score, 4)})

    pontuados.sort(key=lambda d: d["score"], reverse=True)
    return [d for d in pontuados[:top_k] if d["score"] >= minimo]


def formatar_contexto(documentos: list) -> str:
    if not documentos:
        return "Nenhum documento relevante foi encontrado na base de conhecimento."
    partes = [f"## {doc['titulo']} (fonte: {doc['fonte']})\n{doc['conteudo']}" for doc in documentos]
    return "\n\n".join(partes)