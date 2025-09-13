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
        avaliacao_payload = avaliacao_data.model_dump()

        # Converter a data para o padrao json
        avaliacao_payload['data'] = avaliacao_payload['data'].isoformat()

        # Convertendo os id em strings para que garata compartibilidade
        avaliacao_payload['id_disciplina'] = str(avaliacao_payload['id_disciplina'])
        avaliacao_payload['id_coordenador'] = str(avaliacao_payload['id_coordenador'])

        response = supabase.table("avaliacao").insert(avaliacao_payload).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Erro ao cadatrar a avaliacao")

        return response.data[0]

    except Exception as e:
        if "violates foreig key constraint" in str(e).lower():
            if "fk_disciplina" in str(e).lower():
                raise HTTPException(status_code=404,detail=f"A displina com id '{avaliacao_data.id_disciplina}' não foi encotrado")
            if "fk_coordenador" in str(e).lower():
                raise HTTPException(status_code=404,detail=f"A coordenador com id '{avaliacao_data.id_coordenador}' não foi encotrado")

        raise HTTPException(status_code=400, detail=str(e))

### ENDPOINT PARA CONSULTAR AS AVALIAÇÃO USANDO O ID ###
@router.get("/{avalicao_id}", response_model=Avaliacao)
def get_avaliacao(avaliacao_id: uuid.UUID):
    try:
        response = supabase.table("avaliacao").select("*").eq('id_avaliacao', str(avaliacao_id)).single().execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Avaliação não encotrada.")

        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOIN PARA ATUALIZAR UMA AVALIAÇÃO ###
@router.put("/{avaliacao_id}", response_model=Avaliacao)
def update_avaliacao(avaliacao_id: uuid.UUID, avaliacao_data: AvaliacaoUpdate):
    try:
        update_payload = avaliacao_data.model_dump(exclude_unset=True)

        # Se for necessario atualizar a data, converte a data para o padrao json
        if 'data' in update_payload:
            update_payload['data'] = update_payload['data'].isoformat()

        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

        if 'id_coordenador' in update_payload:
            update_payload['id_coordenador'] = str(update_payload['id_coordenador'])

        response = supabase.table('avaliacao').update(update_payload).eq('id_avaliacao', str(avaliacao_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, datail="Avaliação não encontrada para atualização.")

        return response.data[0]
    except Exception as e:
        if "violates foreign key constraint" in str(e).lower() and "fk_coordenador" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"O novo coordenador com id '{avaliacao_data.id_coordenador}' não foi encontrado.")

        raise HTTPException(status_code=500, detail=str(e))

### ENDPOIN PARA DELETAR UMA AVALIACAO ###
@router.delete("/{avaliacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_avaliacao(avaliacao_id: uuid.UUID):
    try:

        response = supabase.table('avaliacao').delete().eq('id_avaliacao', str(avaliacao_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Avaliação não encontrada para deletar")

        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

