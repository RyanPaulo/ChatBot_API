from fastapi import APIRouter, HTTPException, status
from ..supabase_client import supabase
from ..schemas.sch_curso import Curso, CursoCreate, CursoUpadate
import uuid
import json

# --- ROUTER CURSO ---

router = APIRouter(
    prefix="/curso",
    tags=["Curso"]
)

# Função para simplificar a converção dos topicos
def convert_json_fields(db_data: dict) -> dict:
    if isinstance(db_data.get('modalidade'), str):
        db_data['modalidade'] = json.loads(db_data['modalidade'])

    return db_data


### ENDPOINT PARA CADASTRAR OS CURSOS ###
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Curso)
def create_curso(item: CursoCreate):
    try:
        # Converte o objeto Pydantic para um dicionário
        create_payload = item.model_dump()

        # Converter a lista para o padrao json
        if 'modalidade' in create_payload:
            create_payload['modalidade'] = json.dumps(create_payload['modalidade'])

        # Insere os dados na tabela 'MensagemAluno'
        db_response = supabase.table("curso").insert(create_payload).execute()

        if not db_response.data:
            raise HTTPException(status_code=500, detail="Erro ao cadastrar o Curso.")

        db_data = db_response.data[0]

        return convert_json_fields(db_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

### ENDPOINT PARA CONSULTAR OS CRONOGRAMA USANDO O ID ###
@router.get("/{curso_id}", response_model=Curso)
def get_curso(curso_id: uuid.UUID):
    try:
        db_response = supabase.table("curso").select("*").eq('id_curso', str(curso_id)).single().execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail="Curso não encotrada.")

        db_data = db_response.data

        return convert_json_fields(db_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA ATUALIZAR UM ITEM DE CONHECIMENTO ###
@router.put("/{curso_id}", response_model=Curso)
def update_conhecimento(curso_id: uuid.UUID, curso_data: CursoUpadate):
    try:
        update_payload = curso_data.model_dump(exclude_unset=True)

        # Converter a lista para o padrao json
        if 'modalidade' in update_payload:
            update_payload['modalidade'] = json.dumps(update_payload['modalidae'])

        db_response = supabase.table('curso').update(update_payload).eq('id_curso', str(curso_id)).execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail=f"Curso com o ID '{curso_id}' não encontrado para atualização.")

        db_data = db_response.data[0]

        return convert_json_fields(db_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA DELETAR UM CRONOGRAMA USANDO O ID ###
@router.delete("/{curso_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_curso(curso_id: uuid.UUID):
    try:
        db_response = supabase.table('curso').delete().eq('id_curso', str(curso_id)).execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail="Curso não encotrado para deletar.")

        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




