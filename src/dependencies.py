from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from .supabase_client import supabase

# --- DEPENDENCIES DE AUTENTICACAO ---

# Configuração do esquema de autenticação Bearer
security = HTTPBearer()


### DEPENDENCIA PARA OBTER USUARIO AUTENTICADO ###
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependência para verificar o token e obter os dados do usuário autenticado.
    Retorna um dicionário com id, email, name e role do usuário.
    """
    try:
        token = credentials.credentials
        
        # Valida o token e obtém os dados do usuário
        user_response = supabase.auth.get_user(token)
        
        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido ou expirado."
            )
        
        user_metadata = user_response.user.user_metadata
        user_role = user_metadata.get("role", "anonimo")
        
        return {
            "id": user_response.user.id,
            "email": user_response.user.email,
            "name": user_metadata.get("name", None),
            "role": user_role
        }
    
    except Exception as e:
        # Se houver qualquer erro na validação do token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou não fornecido."
        )


### DEPENDENCIA PARA VERIFICAR ROLE DO USUARIO ###
def require_role(allowed_roles: List[str]):
    """
    Factory function que retorna uma dependência para verificar se o usuário tem um dos roles permitidos.
    
    Args:
        allowed_roles: Lista de roles permitidos (ex: ["admin", "coordenador"])
    
    Returns:
        Uma dependência que verifica o role do usuário
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role", "anonimo")
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Roles permitidos: {', '.join(allowed_roles)}. Seu role: {user_role}"
            )
        
        return current_user
    
    return role_checker


### DEPENDENCIAS PRE-CONFIGURADAS PARA ROLES COMUNS ###
require_admin = require_role(["admin"])
require_coordenador = require_role(["coordenador"])
require_professor = require_role(["professor"])  # Professores têm role "professor"
require_admin_or_coordenador = require_role(["admin", "coordenador"])
require_admin_or_coordenador_or_professor = require_role(["admin", "coordenador", "professor"])
require_aluno = require_role(["aluno"])
require_admin_or_aluno = require_role(["admin" , "aluno"])
require_all = require_role(["admin", "coordenador", "professor", "aluno"])


