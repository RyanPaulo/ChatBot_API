
from typing import List, Optional
from datetime import date, time
from fastapi import APIRouter, HTTPException, status
from ..supabase_client import supabase
from ..schemas.sch_avaliacao import AvaliacaoCreate, Avaliacao, AvaliacaoUpdate
import uuid

# --- ROUTER AVALIACAO ---

router = APIRouter(
    prefix="/avaliacao",
    tags=["Avaliação"]
)


### ENDPOINT PARA CADASTRAR AVALIACAO ###
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Avaliacao)
def crete_avaliacao(avaliacao_data: AvaliacaoCreate):
    try:
        # Converte os dados do Pydantic para um dicionário
        payload = avaliacao_data.model_dump()

        # Converte campos de data/hora/uuid para string, se existirem
        for key, value in payload.items():
            if isinstance(value, (date, time, uuid.UUID)):
                payload[key] = str(value)
        
        response = supabase.table("avaliacao").insert(payload).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Erro ao criar a avaliação.")

        return response.data[0]

    except Exception as e:
        if "violates foreign key constraint" in str(e).lower():
            raise HTTPException(status_code=404, detail="A disciplina ou o aplicador especificado não foi encontrado.")
        raise HTTPException(status_code=400, detail=str(e))

### ENDPOINT PARA CONSULTAR AS AVALIAÇÃO USANDO O ID ###
# @router.get("/get_avaliacao/{avalicao_id}", response_model=Avaliacao)
# def get_avaliacao(avaliacao_id: uuid.UUID):
    try:
        response = supabase.table("avaliacao").select("*").eq('id_avaliacao', str(avaliacao_id)).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Avaliação não encotrada.")

        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA CONSULTAR AS AVALIAÇÕES POR DISCIPLINA ###
@router.get("/disciplina/{disciplina_id}", response_model=List[Avaliacao])
def get_avaliacoes_por_disciplina(disciplina_id: uuid.UUID):
    try:
        response = supabase.table("avaliacao").select("*").eq("id_disciplina", str(disciplina_id)).execute()
        
        # Retorna a lista de dados (pode ser uma lista vazia, o que é um resultado válido)
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA ATUALIZAR UMA AVALIAÇÃO POR TIPO E DISCIPLINA ###
@router.put("/disciplina/{disciplina_id}/tipo/{tipo_avaliacao}", response_model=Avaliacao)
def update_avaliacao_por_tipo_e_disciplina(
    disciplina_id: uuid.UUID, 
    tipo_avaliacao: str, # Recebemos como string simples da URL
    avaliacao_data: AvaliacaoUpdate
):
    try:
        # Pega apenas os campos que foram enviados na requisição
        payload = avaliacao_data.model_dump(exclude_unset=True)

        if not payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

        # Converte campos de data/hora/uuid para string, se existirem
        for key, value in payload.items():
            if isinstance(value, (date, time, uuid.UUID)):
                payload[key] = str(value)

        # A "mágica" está aqui: encadeamos dois .eq() para criar um "WHERE ... AND ..."
        response = supabase.table("avaliacao").update(payload).eq(
            "id_disciplina", str(disciplina_id)
        ).eq(
            "tipo_avaliacao", tipo_avaliacao.upper() # Usamos .upper() para garantir consistência (ex: 'np1' vira 'NP1')
        ).execute()

        if not response.data:
            raise HTTPException(
                status_code=404, 
                detail=f"Nenhuma avaliação do tipo '{tipo_avaliacao.upper()}' encontrada para a disciplina especificada."
            )

        # O Supabase retorna uma lista de registros atualizados, pegamos o primeiro.
        return response.data[0]
        
    except Exception as e:
        # Re-lança a exceção se já for uma HTTPException
        if isinstance(e, HTTPException):
            raise e
        # Captura outros erros genéricos
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOIN PARA ATUALIZAR UMA AVALIAÇÃO ###
@router.delete("/{avaliacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_avaliacao(avaliacao_id: uuid.UUID):
    """
    Deleta uma avaliação específica.
    """
    try:
        response = supabase.table("avaliacao").delete().eq("id_avaliacao", str(avaliacao_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Avaliação não encontrada.")

        return # Retorna uma resposta vazia com status 204
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

