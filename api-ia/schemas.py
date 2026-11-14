from typing import Literal, Optional
from pydantic import BaseModel, Field


class PerfilProdutor(BaseModel):
    nome: str = Field(min_length=1, max_length=80)
    caf_ativo: bool
    categoria: Literal["agricultor_familiar", "reforma_agraria", "indigena", "quilombola"]
    finalidade: Optional[Literal["investimento", "maquinas", "habitacao"]] = None
    valor_desejado: Optional[float] = Field(default=None, gt=0)


class ChatRequest(BaseModel):
    pergunta: str = Field(min_length=1, max_length=1000)
    perfil: PerfilProdutor
    conversaId: Optional[str] = None


class FonteOut(BaseModel):
    fonte: str
    titulo: str
    score: float


class ChatResponse(BaseModel):
    resposta: str
    conversaId: str
    fontes: list[FonteOut] = []
    ferramentasUsadas: list[str] = []