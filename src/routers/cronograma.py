from fastapi import APIRouter, HTTPException, status
from ..supabase_client import supabase
from ..schemas.sch_cronograma import CronogramaCreate, Cronograma, CronogramaUpdate
import uuid

# --- ROUTER CRONOGRAMA ---

router = APIRouter(
    prefix="/cronograma",
    tags=["cronograma"]
)


### ENDPOINT PARA REGISTRAR CRONOGRAMA ###
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Cronograma)
def create_cronograma(cronograma_data: CronogramaCreate):
    try:
        cronograma_payload = cronograma_data.model_dump()

        # Converter as datas para o padrao json
        cronograma_payload['data_inicio_semestre'] = cronograma_payload['data_inicio_semestre'].isoformat()
        cronograma_payload['data_fim_semestre'] = cronograma_payload['data_fim_semestre'].isoformat()

        # Converter as horas para o padrao json
        cronograma_payload['hora_inicio'] = cronograma_payload['hora_inicio'].isoformat()
        cronograma_payload['hora_fim'] = cronograma_payload['hora_fim'].isoformat()

        # Convertendo os id em strings para que garata compartibilidade
        cronograma_payload['id_disciplina'] = str(cronograma_payload['id_disciplina'])


        db_response = supabase.table("cronograma").insert(cronograma_payload).execute()

        if not db_response.data:
            raise HTTPException(status_code=500, detail="Erro ao cadatrar a cronograma")

        return db_response.data[0]
    except Exception as e:
        if "violates foreign key constraint" in str(e).lower():
            detail = "A disciplina associado não foi encontrado."
            raise HTTPException(status_code=404, detail=detail)
        raise HTTPException(status_code=400, detail=str(e))

#### ENDPOINT PARA CONSULTAR OS CRONOGRAMA USANDO O ID ####
@router.get("/get_cronograma_id/{cronograma_id}", response_model=Cronograma)
def get_cronograma(cronograma_id: uuid.UUID):
    try:
        db_response = supabase.table("cronograma").select("*").eq('id_cronograma', str(cronograma_id)).single().execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail="Cronograma não encotrada.")

        return db_response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

##### ENDPOINT PARA ATUALIZAR O CRONOGRAMA USANDO O ID ####
@router.put("/updade/{cronograma_id}", response_model=Cronograma)
def update_cronograma(cronograma_id: uuid.UUID, cronograma_data: CronogramaUpdate):
    try:
        update_payload = cronograma_data.model_dump(exclude_unset=True)

        # ifs para converster data e hora para o padrao json
        if 'data_inicio_semestre' in update_payload:
            update_payload['data_inicio_semestre'] = update_payload['data_inicio_semestre'].isoformat()

        if 'data_fim_semestre' in update_payload:
            update_payload['data_fim_semestre'] = update_payload['data_fim_semestre'].isoformat()

        if 'hora_inicio' in update_payload:
            update_payload['hora_inicio'] = update_payload['hora_inicio'].isoformat()

        if 'hora_fim' in update_payload:
            update_payload['hora_fim'] = update_payload['hora_fim'].isoformat()

        if 'id_disciplina' in update_payload:
            update_payload['id_disciplina'] = update_payload['id_disciplina'].isoformat()

        # Para filtro de erros
        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

        db_response = supabase.table('cronograma').update(update_payload).eq('id_cronograma', str(cronograma_id)).execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail="Cronograma não encontrada para atualização.")

        return db_response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

##### ENDPOINT PARA DELETAR UM CRONOGRAMA USANDO O ID ####
@router.delete("/delete/{cronograma_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cronograma(cronograma_id: uuid.UUID):
    try:

        db_response = supabase.table('cronograma').delete().eq('id_cronograma', str(cronograma_id)).execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail="Cronograma não encontrado para deletar")

        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
