from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from ..supabase_client import supabase
from ..schemas.sch_base_conhecimento import BaseConhecimento, BaseConhecimentoCreate, BaseConhecimentoUpdate
import uuid
import json

# --- ROUTER BASE DE CONHECIMENTO PARA O RASA AI ---

router = APIRouter(
    prefix="/conhecimento",
    tags=["Base de Conhecimento"]
)

# Função para simplificar a converção das respostas do banco de volta para o formato do schema
def convert_json_fields(db_data: dict) -> dict:
    # Converte campos JSONB de string para lista em um dicionário.
    if isinstance(db_data.get('palavra_chave'), str):
        db_data['palavra_chave'] = json.loads(db_data['palavra_chave'])
    if isinstance(db_data.get('visivel_para'), str):
        db_data['visivel_para'] = json.loads(db_data['visivel_para'])
    return db_data

### ENDPOINT PARA CADASTRAR CONHECIMENTO ###
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=BaseConhecimento)
def create_conhecimento(item: BaseConhecimentoCreate):
    try:
        payload = item.model_dump()

        if 'palavra_chave' in payload:
            payload['palavra_chave'] = json.dumps(payload['palavra_chave'])
        if 'visivel_para' in payload:
            payload['visivel_para'] = json.dumps(payload['visivel_para'])

        if payload.get('id_disciplina'):
            payload['id_disciplina'] = str(payload['id_disciplina'])

        response = supabase.table("baseconhecimento").insert(payload).execute()

        # Filtro de erro, para um mensagem mais clara
        if not response.data:
            error_detail = "Erro ao inserir na base de conhecimento"

            try:
                api_error = response.model_dump()
                if api_error and 'message' in api_error:
                    error_detail = api_error['message']
            except Exception:
                pass

            raise HTTPException(status_code=500, detail=error_detail)


        db_data = response.data[0]

        return convert_json_fields(db_data)

    except Exception as e:
        # Tratamento de erro para chave estrangeira (se o disciplina não existir)
        if "violates foreign key constraint" in str(e).lower() and "fk_disciplina" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"A disciplina com ID '{item.id_disciplina}' não foi encotrada.")
        raise HTTPException(status_code=400, detail=str(e))

### ENDPOINT PARA LISTA TODOS OS ITEM DE CONHECIMENTO ###
@router.get("/", response_model=list[BaseConhecimento])
def list_conhecimento():
    try:
        response = supabase.table("baseconhecimento").select("*").order("criado_em", desc=True).execute()


        processed_data = [convert_json_fields(item) for item in response.data]
        return processed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA CONSULTA UM ITEM DE CONHECIMENTO ###
@router.get("/{item_id}", response_model=BaseConhecimento)
def get_conhecimento(item_id: uuid.UUID):
    try:
        response = supabase.table("baseconhecimento").select("*").eq('id_conhecimento', str(item_id)).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Item de conhecimento não encontrado.")

        db_data = response.data
        return convert_json_fields(db_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA ATUALIZAR UM ITEM DE CONHECIMENTO ###
@router.put("/{item_id}", response_model=BaseConhecimento)
def update_conhecimento(item_id: uuid.UUID, item: BaseConhecimentoUpdate):
    try:
        payload = item.model_dump(exclude_unset=True)

        if not payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

        if payload.get('id_disciplina'):
            payload['id_disciplina'] = str(payload['id_disciplina'])

        payload['atualizado_em'] = datetime.now().isoformat()

        response = supabase.table("baseconhecimento").update(payload).eq('id_conhecimento', str(item_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail=f"item com ID '{item_id}' não encontrado.")


        db_data = response.data[0]

        return convert_json_fields(db_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA DELETAR UM ITEM DE CONHECIMENTO ###
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conhecimento(item_id: uuid.UUID):
    try:
        response = supabase.table("baseconhecimento").delete().eq('id_conhecimento', str(item_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail=f"Item com ID '{item_id}' não encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))