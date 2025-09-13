from typing import Optional, List
from pydantic import BaseModel, Field
import uuid

### ESQUEMA DE DADOS 'CURSO' ###

#Schema base com os campos que podem ser criados
class CursoBase(BaseModel):
    nome_curso: str
    duracao: int
    modalidade: List[str] = Field(default_factory=list)
    formacao: str

# Schema para a criação da tabela 'Curso'
class CursoCreate(CursoBase):
    pass

# Para representar um registro completo do banco de dados
class Curso(CursoBase):
    id_curso: uuid.UUID

    class Config:
        from_attributes = True


# Schema para atualização do Curso
class CursoUpadate(BaseModel):
    nome_curso: Optional[str] = None
    duracao: Optional[int] = None
    modalidade: Optional[List[str]] = Field(default_factory=list)
    formacao: Optional[str]