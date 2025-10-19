from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid

### Esquema de dados 'Aluno' ###

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str