from datetime import datetime
from pydantic import BaseModel, Field, root_validator
from typing import Optional, List
import uuid


### Esquema de dados 'Base de Conhecimento' para o chatbot acessar ###

# Schema da base com os campos que podem ser criados ou atualizados
class BaseConhecimentoBase(BaseModel):
    pergunta_principal: str
    resposta: str
    palavra_chave: List[str] = Field(default_factory=list)
    categoria: Optional[str] = None
    # visivel_para: List[str] = Field(default_factory=list, description="Ex: ['aluno', 'professor']")
    visivel_para: List[str] = Field(default_factory=list)
    status: str = "rascunho"
    id_disciplina: Optional[uuid.UUID] = None


# Esquema para a criado de uma no base de conhecimento
class BaseConhecimentoCreate(BaseConhecimentoBase):
    pass


# Para representar um registro completo do banco de dados
class BaseConhecimento(BaseConhecimentoBase):
    id_conhecimento: uuid.UUID
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


# Esquema para atualizar a base de conhecimento (Todos os campos sao opicional)
class BaseConhecimentoUpdate(BaseModel):
    pergunta_principal: Optional[str] = None
    resposta: Optional[str] = None
    palavra_chave: Optional[List[str]] = None
    categoria: Optional[str] = None
    visivel_para: Optional[List[str]] = None
    status: Optional[str] = None
    id_disciplina: Optional[uuid.UUID] = None