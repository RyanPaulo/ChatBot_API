from fastapi import APIRouter, HTTPException, status
from ..supabase_client import supabase
from ..schemas.sch_disciplina import DisciplinaCreate, Disciplina, DisciplinaUpdate
import uuid


router = APIRouter(
    prefix="/disciplinas",
    tags=["Disciplina"]
)


### ENDPOINT PARA CASDATRAR DISCIPLINAS #####
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Disciplina)
def crete_disciplina(disciplina_data: DisciplinaCreate):
    try:
        disciplina_payload = disciplina_data.model_dump()

        disciplina_payload['id_professor'] = str(disciplina_payload['id_professor'])

        response = supabase.table("disciplina").insert(disciplina_payload).execute()

        if not response.data:
            raise HTTPException(status_code=500, detail="Erro ao cadastrar a disciplina")

        return response.data[0]

    except Exception as e:
        if "violates foreig key constraint" in str(e).lower():
            raise HTTPException(status_code=404, datail=f"O professor com ID '{disciplina_data.id_professor}' não foi encontrado.")
        raise HTTPException(status_code=400, detail=str(e))

##### ENDPOINT PARA CONSULTAR AS DISCIPLINAS USANDO O ID ####
@router.get("/{disciplina}", response_model=Disciplina)
def get_discilina(disciplina_id: uuid.UUID):
    try:
        response = supabase.table("disciplina").select("*").eq('id_disciplina', str(disciplina_id).single().execute())
        if not response.data:
            raise HTTPException(status_code=404, detail="Disiciplina não encontrada.")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA ATUALIZAR AVALIACAO ###
@router.put("/{disciplina_id}", response_model=Disciplina)
def update_disciplina(disciplina_id: uuid.UUID, disciplina_data: DisciplinaUpdate):
    try:
        update_payload = disciplina_data.model_dump(exclude_unset=True)

        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização")

        if 'id_professor' in update_payload:
            update_payload['id_professor'] = str(update_payload['id_professor'])

        response= supabase.table('disciplina').update(update_payload).eq('id_disciplina', str(disciplina_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada para atualização.")

        return response.data[0]
    except Exception as e:
        if "violates foreig key constraint" in str(e).lower() and "fk_professor" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"O novo professor com id '{disciplina_data.id_professor}' não foi encontrado.")

        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA DELETAR AVALIACAO ###
@router.delete("/{desciplina_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disciplina(disciplina_id: uuid.UUID):
    try:
        response = supabase.table('disciplina').delete().eq('id_disciplina', str(disciplina_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Avaliação nãoi encotrado para deletar")

        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

