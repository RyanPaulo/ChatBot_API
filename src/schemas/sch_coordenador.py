from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid


### Esquema de dados 'Coordenador' ###
class CoordenadorBase(BaseModel):
    id_funcional: str
    nome_coordenador: str
    sobrenome_coordenador: str
    email_institucional: EmailStr
    departamento: str

class CoordenadorCreate(CoordenadorBase):
    password: str

class Coordenador(CoordenadorBase):
    id: uuid.UUID

    class Config:
        from_attributes = True

class CoordenadorUpdate(BaseModel):
    nome_coordenador: Optional[str] = None
    sobrenome_coordenador: Optional[str] = None
    email_institucional: Optional[EmailStr] = None
    departamento: Optional[str] = None