from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


### Esquema de dados 'Professor' ###

class ProfessorBase(BaseModel):
    id_funcional: str
    nome_professor: str
    sobrenome_professor: str
    email_institucional: EmailStr

class ProfessorCreate(ProfessorBase):
    password: str

class Professor(ProfessorBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class ProfessorUpdate(BaseModel):
    nome_professor: Optional[str] = None
    sobrenome_professor: Optional[str] = None
    email_institucional: Optional[EmailStr] = None