from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from gotrue.helpers import model_dump

from ..supabase_client import supabase
from typing import List
from ..schemas.sch_base_conhecimento import BaseConhecimento, BaseConhecimentoCreate, BaseConhecimentoUpdate
import uuid
import json



router = APIRouter(
    prefix="/conhecimento",
    tags=["Base de Conhecimento"]
)

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

        response = supabase.table("BaseConhecimento").insert(payload).execute()

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

        return response.data[0]

    except Exception as e:
        if "violates foreign key constraint" in str(e).lower() and "fk_disciplina" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"A disciplina com ID '{item.id_disciplina}' não foi encotrada.")
        raise HTTPException(status_code=400, detail=str(e))


### ENDPOINT PARA LISTA TODOS OS ITEM DE CONHECIMENTO ###
@router.get("/", response_model=list[BaseConhecimento])
def list_conhecimento():
    try:
        response = supabase.table("BaseConhecimento").select("*").order("criado_em", desc=True).execute()

        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA CONSULTA UM ITEM DE CONHECIMENTO ###
@router.get("/{item_id}", response_model=BaseConhecimento)
def get_conhecimento(item_id: uuid.UUID):
    try:
        response = supabase.table("BaseConhecimento").select("*").eq('id_conhecimento', str(item_id)).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Item de conhecimento não encontrado.")
        return response.data
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

        response = supabase.table("BaseConhecimento").update(payload).eq('id_conhecimento', str(item_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail=f"item com ID '{item_id}' não encontrado.")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


### ENDPOINT PARA DELETAR UM ITEM DE CONHECIMENTO ###
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conhecimento(item_id: uuid.UUID):
    try:
        response = supabase.table("BaseConhecimento").delete().eq('id_conhecimento', str(item_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail=f"Item com ID '{item_id}' não encontrado.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))