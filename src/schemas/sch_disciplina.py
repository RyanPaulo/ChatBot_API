from pydantic import BaseModel
from typing import Optional
import uuid

### Esquema de dados 'Disciplina' ###

class DisciplinaBase(BaseModel):
    nome_disciplina: str
    codigo: str
    semestre: str
    id_professor: uuid.UUID

class DisciplinaCreate(DisciplinaBase):
    pass # Pass - por que nao precisa de mais nenhum campo extra alem do DisciplinaBase


class Disciplina(DisciplinaBase):
    id_disciplina: uuid.UUID

    class Config:
        from_attributes = True

class DisciplinaUpdate(BaseModel):
    nome_disciplina: Optional[str] = None
    codigo: Optional[str] = None
    semestre: Optional[str] = None
    id_professor: Optional[uuid.UUID] = None

