from fastapi import APIRouter, HTTPException, status, Depends
from src.supabase_client import supabase
from ..schemas.sch_professor import ProfessorCreate, Professor, ProfessorUpdate
from ..dependencies import require_admin_or_coordenador, require_all, require_admin_or_coordenador_or_professor
from typing import List

# --- ROUTER PROFESSORES ---

router = APIRouter(
    prefix="/professores",
    tags=["Professores"]
)

### ENDPOINT PARA CADASTRAR PROFESSORES ###
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Professor)
def create_professor(professor_data: ProfessorCreate): #, current_user: dict = Depends(require_admin_or_coordenador)
    try:
        # Para gravar email e senha dos professores no auth do supabase
        auth_response = supabase.auth.sign_up({
            "email": professor_data.email_institucional,
            "password": professor_data.password,
            "options": {
                "data": {
                    "name": f"{professor_data.nome_professor} {professor_data.sobrenome_professor}",
                    "role": "professor"
                }
            }
        })
        user_id = auth_response.user.id

        # Preparar os dados dos professores para inserir na tabela "Professor"
        professor_profile_data = professor_data.model_dump(exclude={"password", "disciplina_nomes"})
        professor_profile_data["id"] = user_id

        # Para converter os time
        professor_profile_data['atendimento_hora_inicio'] = professor_profile_data['atendimento_hora_inicio'].isoformat()
        professor_profile_data['atendimento_hora_fim'] = professor_profile_data['atendimento_hora_fim'].isoformat()

        #Inserir o perfil do Professor na tabela "Professor"
        db_response = supabase.table("professor").insert(professor_profile_data).execute()

        # Verificar se o processo foi bem sucedido
        if not db_response.data:
            raise  HTTPException(status_code=500, detail="Erro ao salvar o perfil do professor")

        # created_professor =  db_response.data[0]

        if professor_data.disciplina_nomes:
            disciplinas_ids_response = supabase.table("disciplina").select("id_disciplina", "nome_disciplina").in_("nome_disciplina", professor_data.disciplina_nomes).execute()

            disciplinas_encontrada = disciplinas_ids_response.data
            if len(disciplinas_encontrada) != len(professor_data.disciplina_nomes):
                # Identificar qual disciplina não foi encontrada para um erro mais claro
                nomes_encontrado = {d['nome_disciplina'] for d in disciplinas_encontrada}
                missing_names = [name for name in professor_data.disciplinas_nomes if name not in nomes_encontrado]
                raise HTTPException(status_code=404,
                                    detail=f"As seguintes disciplinas não foram encontradas: {', '.join(missing_names)}")

                # Preparar os registros para a tabela associativa
            associations_to_create = [
                {"id_professor": user_id, "id_disciplina": disciplina['id_disciplina']}
                for disciplina in disciplinas_encontrada
            ]

            # 3c. Inserir todas as associações de uma vez
            if associations_to_create:
                supabase.table("professordisciplina").insert(associations_to_create).execute()

        created_professor_dict = db_response.data[0]

        professor_obj = Professor.model_validate(created_professor_dict)
        return professor_obj

    except Exception as e:
        #Se algo deu errado após a criação do usuário no Auth, deleta o usuário.
        if user_id:
            try:
                auth_delete_response = supabase.auth.admin.delete_user(user_id)
            except Exception as admin_exc:
                print(f"ERRO CRITICO: Falha ao fazer rollback do usuario {user_id}. Erro: {admin_exc}")
        if "User already registered" in str(e):
            raise HTTPException(status_code=409, detail="Este e-mail ja esta cadastrados.")

        if isinstance(e, HTTPException):
            raise e
        raise  HTTPException(status_code=400, detail=str(e))

### ENDPOINT PARA LISTAR TODOS OS PROFESSORES CADASTRADOS NO BD ###
@router.get("/lista_professores/", response_model=List[Professor])
def get_all_professores(): #current_user: dict = Depends(require_all)
    try:
        response = supabase.table("professor").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA ATUALIZAR CADASTRO DO PROFESSORES ###
@router.put("/update/{id}", response_model=Professor)
def update_professor(id: str, professor_update_data: ProfessorUpdate):# , current_user: dict = Depends(require_admin_or_coordenador_or_professor)
    try:

        update_payload = professor_update_data.model_dump(exclude_unset=True)

        if 'atendimento_hora_inicio' in update_payload:
            update_payload['atendimento_hora_inicio'] = update_payload['atendimento_hora_inicio'].isoformat()

        if 'atendimento_hora_fim' in update_payload:
            update_payload['atendimento_hora_fim'] = update_payload['atendimento_hora_fim'].isoformat()

        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

        response = supabase.table('professor').update(update_payload).eq('id_funcional', id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Professor não encontrado para atualização.")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINR PARA DELETAR PROFESSORES ###
@router.delete("/detele/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_professor(id: str, current_user: dict = Depends(require_admin_or_coordenador)):
    try:
        response = supabase.table("professor").select("id").eq("id_funcional", id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Professor não encontrado para deletar.")

        professor_id = response.data[0]['id']

        delete_response = supabase.table('professor').delete().eq('id', professor_id).execute()

        if not delete_response.data:
            raise HTTPException(status_code=500, detail="Falha ao deletar o perfil do professor. A operação foi abortada.")

        auth_delete_response = supabase.auth.admin.delete_user(professor_id)
        return

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



