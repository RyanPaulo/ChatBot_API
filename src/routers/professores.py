from fastapi import APIRouter, HTTPException, status
from src.supabase_client import supabase
from src.schemas.sch_professor import ProfessorCreate, Professor, ProfessorUpdate

# --- ROUTER PROFESSORES ---

router = APIRouter(
    prefix="/professores",
    tags=["Professores"]
)

# **** ENDPOINT PARA CADASTRAR PROFESSORES ****
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Professor)
def create_professor(professor_data: ProfessorCreate):
    try:
        # Para gravar email e senha dos professores no auth do supabase
        auth_response = supabase.auth.sign_up({
            "email": professor_data.email_institucional,
            "password": professor_data.password
        })
        user_id = auth_response.user.id

        # Preparar os dados dos professores para inserir na tabela "Professor"
        professor_profile_data = professor_data.model_dump(exclude={"password"})
        professor_profile_data["id"] = user_id

        #Inserir o perfil do Professor na tabela "Professor"
        db_response = supabase.table("professor").insert(professor_profile_data).execute()

        # Verificar se o processo foi bem sucedido
        if not db_response.data:
            raise  HTTPException(status_code=500, detail="Erro ao salvar o perfil do professor")

        return db_response.data[0]

    except Exception as e:
        raise  HTTPException(status_code=400, detail=str(e))

# **** ENDPOINT PARA ATUALIZAR CADASTRO DO PROFESSORES ****
@router.put("/{id}", response_model=Professor)
def update_professor(id: str, professor_update_data: ProfessorUpdate):
    try:

        update_payload = professor_update_data.model_dump(exclude_unset=True)

        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

        response = supabase.table('professor').update(update_payload).eq('id_funcional', id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Professor não encontrado para atualização.")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# **** ENDPOINR PARA DELETAR PROFESSORES ****
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professor(id: str):
    try:
        response = supabase.table('professor').delete().eq('id_funcional', id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Professor não encontrado para deletar.")

        return

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
