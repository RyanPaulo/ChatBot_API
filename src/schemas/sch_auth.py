from pydantic import BaseModel, EmailStr

### Esquema de dados 'Aluno' ###

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str