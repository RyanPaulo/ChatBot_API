from fastapi import APIRouter, HTTPException, status
from src.supabase_client import supabase
from src.schemas.sch_aluno import AlunoCreate, Aluno, AlunoUpdate

# --- ROUTER ALUNOS ---

router = APIRouter(
    prefix="/alunos", # Definir coordenadas do URL
    tags=["Alunos"]
)

# **** ENDPOINT PARA CASDATRAR ALUNO ****
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Aluno)
def create_aluno(aluno_data: AlunoCreate):
    try:
        # Criar o usuario no Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": aluno_data.email_institucional,
            "password": aluno_data.password
        })
        user_id = auth_response.user.id

        # Prepara os dados do aluno para inserção na tabela "Aluno"
        aluno_profile_data = aluno_data.model_dump(exclude={"password"})
        aluno_profile_data["id"] = user_id

        # Inserir o perfil do aluno na tabela Aluno
        db_response = supabase.table("aluno").insert(aluno_profile_data).execute()

        # Verifica se a inserção foi bem-sucedida
        if not db_response.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar o perfil do aluno.")
        return db_response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# **** ENDPOINT PARA ATUALIZAR UM ALUNO ****
# tendo como referencia o RA do aluno
@router.put("/{ra}", response_model=Aluno)
def update_aluno(ra: str, aluno_update_data: AlunoUpdate):
    try:
        # Cria um dicionario apensa com os dados que foram enviados (nâo none)
        update_payload = aluno_update_data.model_dump(exclude_unset=True)

        # Se não houver dados para atualizar, retorne um erro ou a entidade original
        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

        # Executa o update no supabase
        response = supabase.table('aluno').update(update_payload).eq('matricula_ra', ra).execute()

        # Se não encontrar o aluno
        if not response.data:
            raise HTTPException(status_code=404, detail="Aluno não encontrado para atualização.")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# **** ENDPOINT PARA DELETAR UM ALUNO ****
@router.delete("/{ra}", status_code=status.HTTP_204_NO_CONTENT)
def delete_aluno(ra: str):
    # ** Lembrar que essa função não remove o usuário do sistema de autenticação do Supabase.
    try:
        # Executa o delete no Supabase | tabela = aluno | indentificado do aluno = matricula_ra
        response = supabase.table('aluno').delete().eq('matricula_ra', ra).execute()

        # Verifica se algum dado foi retornado (o que segnifica que algo foi deletado)
        if not response.data:
            raise HTTPException(status_code=404, detail="Aluno nao encontrado para deletar.")

        # HTTP 204 nao deve retornar nenhum corpo de resposta
        return

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
