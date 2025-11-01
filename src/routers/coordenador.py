from fastapi import APIRouter, HTTPException, status
from typing import List
from src.supabase_client import supabase
from src.schemas.sch_coordenador import CoordenadorCreate, Coordenador, CoordenadorUpdate

# --- ROUTER COORDENADOR ---

router = APIRouter(
    prefix="/coordenador",
    tags=["Coordenador"]
)

### ENDPOINT PARA CADASTRAR COORDENADOR ###
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Coordenador)
def create_coordenador(coordenador_data: CoordenadorCreate):
    try:
        auth_response = supabase.auth.sign_up({
            "email": coordenador_data.email_institucional,
            "password": coordenador_data.password,
            "options": {
                "data": {
                    "name": f"{coordenador_data.nome_coordenador} {coordenador_data.sobrenome_coordenador}"
                }
            }
        })
        user_id = auth_response.user.id


        coordenador_profile_data = coordenador_data.model_dump(exclude={"password"})
        coordenador_profile_data["id"] = user_id

        # Para converter os time
        coordenador_profile_data['atendimento_hora_inicio'] = coordenador_profile_data['atendimento_hora_inicio'].isoformat()
        coordenador_profile_data['atendimento_hora_fim'] = coordenador_profile_data['atendimento_hora_fim'].isoformat()

        db_response = supabase.table("coordenador").insert(coordenador_profile_data).execute()


        if not db_response.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar o perfil do coordenador")

        return db_response.data[0]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


    # **** ENDPOINT PARA ATUALIZAR CADASTRO DO COORDENADOR ****

### ENDPOINT PARA LISTAR TODOS OS ALUNOS CADASTRADOS NO BD ###
@router.get("/get_list_coordenador/", response_model=List[Coordenador])
def get_all_aluno():
    try:
        response = supabase.table("coordenador").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA ATUALIZAR COORDENADOR ###
@router.put("/updade/{id}", response_model=Coordenador)
def update_coordenador(id: str, coordenador_update_data: CoordenadorUpdate):
    try:

        update_payload = coordenador_update_data.model_dump(exclude_unset=True)

        if 'atendimento_hora_inicio' in update_payload:
            update_payload['atendimento_hora_inicio'] = update_payload['atendimento_hora_inicio'].isoformat()

        if 'atendimento_hora_fim' in update_payload:
            update_payload['atendimento_hora_fim'] = update_payload['atendimento_hora_fim'].isoformat()


        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualiuzação.")

        response = supabase.table('coordenador').update(update_payload).eq('id_funcional', id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Coordenador não encontrado para atualização")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINR PARA DELETAR COORDENADOR ###
@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coordenador(id: str):
    try:
        response = supabase.table('coordenador').select("id").eq('id_funcional', id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Coordenador não encontrado para deletar")


        coordeandor_id = response.data[0]['id']

        delete_response = supabase.table('coordenador').delete().eq('id', coordeandor_id).execute()

        if not delete_response.data:
            raise HTTPException(status_code=500, detail="Falha ao deletar o perfil do aluno. A operação foi abortada.")

        auth_delete_response = supabase.auth.admin.delete_user(coordeandor_id)
        return


    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

