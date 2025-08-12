
from fastapi import APIRouter, HTTPException, status
from src.supabase_client import supabase
from src.schemas.auth import UserLoginSchema


router = APIRouter(
    tags=["Autenticação"]
)

@router.post("/login", status_code=status.HTTP_200_OK)
def user_login(credentials: UserLoginSchema):
    """
    Autentica um usuário usando o serviço de autenticação do Supabase.
    """
    try:
        # Chama a função de login nativa do Supabase
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        # Se o login for bem-sucedido, o Supabase retorna os dados da sessão
        return {
            "message": "Login realizado com sucesso!",
            "access_token": response.session.access_token,
            "user_id": response.user.id,
            "user_email": response.user.email
        }

    except Exception as e:
        # Captura erros de login (e-mail não existe, senha incorreta, etc.)
        # O Supabase geralmente retorna um erro específico que podemos tratar
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro de autenticação: As credenciais são inválidas."
        )