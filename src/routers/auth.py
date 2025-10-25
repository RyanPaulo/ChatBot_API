
from fastapi import APIRouter, HTTPException, status
from src.supabase_client import supabase
from src.schemas.sch_auth import UserLoginSchema


router = APIRouter(
    tags=["Autenticação"]
)

### ENDPOINT PARA AUTENTICAÇÃO DO USUARIO ###
@router.post("/login", status_code=status.HTTP_200_OK)
def user_login(credentials: UserLoginSchema):

    try:
        # Chama a função de login nativa do Supabase
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })

        # Usar o access_token da sessão para buscar os dados completos do usuário.
        user_data_response = supabase.auth.get_user(response.session.access_token)

        user_metadata = user_data_response.user.user_metadata
        user_name = user_metadata.get("name", None)

        # Se o login for bem-sucedido, o Supabase retorna os dados da sessão
        return {
            "message": "Login realizado com sucesso!",
            "access_token": response.session.access_token,
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "name": user_name
            }
        }

    except Exception as e:
        # Captura erros de login (e-mail não existe, senha incorreta, etc.)
        # O Supabase geralmente retorna um erro específico que podemos tratar
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Erro de autenticação: As credenciais são inválidas."
        )

