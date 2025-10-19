from fastapi import APIRouter, HTTPException, status
from src.supabase_client import supabase
from src.schemas.sch_aluno import AlunoCreate, Aluno, AlunoUpdate
import uuid

# --- ROUTER ALUNOS ---

router = APIRouter(
    prefix="/alunos", # Definir coordenadas do URL
    tags=["Alunos"]
)

### ENDPOINT PARA CASDATRAR ALUNO ###
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
        aluno_profile_data['id_curso'] = str(aluno_profile_data['id_curso'])

        # Inserir o perfil do aluno na tabela Aluno
        db_response = supabase.table("aluno").insert(aluno_profile_data).execute()

        # Verifica se a inserção foi bem-sucedida
        if not db_response.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar o perfil do aluno.")

        new_aluno = db_response.data[0]
        id_new_aluno = new_aluno['id']
        id_curso_aluno = new_aluno['id_curso']

        # Buscar os IDs das disciplinas do curso na tabela associativa "CursoDisciplina"
        disciplinas_response = supabase.table("cursodisciplina").select("id_disciplina").eq("id_curso", id_curso_aluno).execute()

        if disciplinas_response.data:
            # Preparar os registros para a tabela AlunoDisciplina
            create_registration = [
                {"id_aluno": id_new_aluno,  "id_disciplina": item['id_disciplina']}
                for item in disciplinas_response.data
            ]

            # Inserir todas as matrículas de uma vez
            if create_registration:
                supabase.table("alunodisciplina").insert(create_registration).execute()

        return new_aluno

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


### ENDPOINT PARA BUSCAR UM ALUNO PELO EMAIL ###
@router.get("/email/{email}", response_model=Aluno)
def get_aluno_by_email(email: str):
    try:
        # Realiza a consulta na tabela "aluno" filtrando pelo email_institucional
        response = supabase.table("aluno").select("*").eq("email_institucional", email).single().execute()

        # Verifica se a busca retornou algum dado
        if not response.data:
            # Se não retornou, o aluno não foi encontrado. Lançamos um erro 404.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nenhum aluno encontrado com o email '{email}'."
            )

        # Se encontrou, retorna os dados do aluno.
        return response.data

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Um erro inesperado ocorreu: {str(e)}"
        )

### ENDPOINT PARA ATUALIZAR UM ALUNO ###
# Utilizando o RA do aluno como referencia o RA do aluno
@router.put("/{ra}", response_model=Aluno)
def update_aluno(ra: str, aluno_update_data: AlunoUpdate):
    try:
        # Cria um dicionario apensa com os dados que foram enviados (nâo none)
        update_payload = aluno_update_data.model_dump(exclude_unset=True)

        #  Buscamos o aluno ANTES de atualizar para saber o curso antigo
        aluno_response = supabase.table("aluno").select("id, id_curso").eq("matricula_ra", ra).single().execute()
        if not aluno_response.data:
            raise HTTPException(status_code=404, detail="Aluno nao encontrado.")

        id_aluno = aluno_response.data['id']
        id_curso_previous = aluno_response.data['id_curso']

        # Verificamos se o curso do aluno está sendo alterado
        new_id_curso = update_payload.get('id_curso', id_curso_previous)
        if isinstance(new_id_curso, uuid.UUID):
            new_id_curso = str(new_id_curso)

        # Atualiza os dados principais do aluno
        if 'id_curso' in update_payload:
            update_payload['id_curso'] = new_id_curso

        db_response = supabase.table('aluno').update(update_payload).eq('id', id_aluno).execute()
        if not db_response.data:
            raise HTTPException(status_code=500, detail="Falha ao atualizar os dados do aluno.")
        aluno_updated = db_response.data[0]

        #Se o curso mudou, sincronizamos as matrículas
        if new_id_curso != id_curso_previous:
            # DELETE: Remove todas as matrículas antigas do aluno
            supabase.table("alunodisciplina").delete().eq("id_aluno", id_aluno).execute()

            # SELECT & INSERT: Busca as disciplinas do novo curso e cria as novas matrículas
            disciplinas_response = supabase.table("disciplina").select("id_disciplina").eq("id_curso", new_id_curso).execute()
            if disciplinas_response.data:
                ra_to_create = [
                    {"id_aluno": id_aluno, "id_disciplina": disciplina['id_disciplina']}
                    for disciplina in disciplinas_response.data
                ]
                if ra_to_create:
                    supabase.table("alunodisciplina").insert(ra_to_create).execute()

        return aluno_updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA DELETAR UM ALUNO ###
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
