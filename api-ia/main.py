import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from assistente import conversar
from schemas import ChatRequest, ChatResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agrocredito-ia")

app = FastAPI(
    title="AgroCrédito IA API",
    description="API de inteligência artificial que orienta pequenos produtores sobre crédito rural.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"mensagem": "AgroCrédito IA API está funcionando."}


@app.get("/saude")
def saude():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(requisicao: ChatRequest):
    try:
        resposta, conversa_id, fontes, ferramentas = conversar(
            requisicao.pergunta,
            requisicao.perfil.model_dump(),
            requisicao.conversaId,
        )
    except Exception:
        logger.exception("Falha ao consultar o modelo de IA")
        raise HTTPException(
            status_code=502,
            detail="Não foi possível consultar o modelo de IA no momento. Tente novamente."
        )
    return ChatResponse(
        resposta=resposta,
        conversaId=conversa_id,
        fontes=fontes,
        ferramentasUsadas=ferramentas,
    )