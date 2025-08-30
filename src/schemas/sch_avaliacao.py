from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
import uuid



### Esquema de dados 'Avaliacao' ###

class AvaliacaoBase(BaseModel):
    topico: str
    data: datetime = Field(..., example="0000-00-00T00:00") # Feild = para criar um molde de preencimento da data
    descricao: str
    id_disciplina: uuid.UUID
    id_coordenador: uuid.UUID


class AvaliacaoCreate(AvaliacaoBase):
    pass

class Avaliacao(AvaliacaoBase):
    id_avaliacao: uuid.UUID

    class Config:
        from_attributes = True

class AvaliacaoUpdate(BaseModel):
    topico: Optional[str] = None
    data: Optional[datetime] = Field(None, example="0000-00-00T00:00")
    descricao: Optional[str] = None
    id_coordenador: Optional[uuid.UUID] = None
