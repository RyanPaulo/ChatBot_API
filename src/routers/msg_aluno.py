from fastapi import APIRouter, HTTPException, status
from ..supabase_client import supabase
from typing import List
from ..schemas.sch_msg_aluno import MensagemAluno, MensagemAlunoCreate, MensagemAlunoUpdate
import uuid
import json

# --- ROUTER MENSAGEM DOS ALUNOS ---

router = APIRouter(
    prefix="/mensagens_aluno",
    tags=["Mensagens de Alunos"]
)

# Função para simplificar a converção dos topicos
def convert_json_fields(db_data: dict) -> dict:
    if isinstance(db_data.get('topico'), str):
        db_data['topico'] = json.loads(db_data['topico'])

    return db_data


### ENDPOINT PARA CADASTRAR UMA MENSAGEM DE ALUNO ###
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MensagemAluno)
def create_mensagem_aluno(item: MensagemAlunoCreate):
    try:
        # Converte o objeto Pydantic para um dicionário
        payload = item.model_dump()

        # Converter a lista para o padrao json
        if 'topico' in payload:
            payload['topico'] = json.dumps(payload['topico'])

        # Converte a data e hora para o formato que é compatível com o Supabase
        payload['data_hora'] = payload['data_hora'].isoformat()

        # Insere os dados na tabela 'MensagemAluno'
        db_response = supabase.table("mensagemaluno").insert(payload).execute()

        if not db_response.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar a mensagem do aluno.")

        db_data = db_response.data[0]

        return convert_json_fields(db_data)

    except Exception as e:

        raise HTTPException(status_code=400, detail=str(e))

### ENDPOINT PARA LISTAR TODAS AS MENSAGENS ###
@router.get("/get_lista_msg/", response_model=List[MensagemAluno])
def list_mensagens_aluno():
    try:
        # Para consulta na tabela 'MensagemAluno'
        response = supabase.table("mensagemaluno").select("*").order("data_hora", desc=True).execute()

        processed_data = [convert_json_fields(item) for item in response.data]
        return processed_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA ATUALIZAR A MENSAGE ###
# Esse endpoint sera usado somente para teste de desenvolvimento
@router.put("/update/{item_id}", response_model=MensagemAluno)
def update_mensagem(item_id: uuid.UUID, item: MensagemAlunoUpdate):
    try:
        payload = item.model_dump(exclude_unset=True)

        # Converte a data e hora para o formato que é compatível com o Supabase
        payload['data_hora'] = payload['data_hora'].isoformat()

        if not payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização.")

        db_response = supabase.table("mensagemaluno").update(payload).eq('id_mensagem', str(item_id)).execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail=f"Item com ID '{item_id}' não encontrado.")

        db_data = db_response.data[0]
        return convert_json_fields(db_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA DELETAR UMA MENSAGEM DE ALUNO ###
# **Esse endpoint sera usado somente para teste de desenvolvimento**
@router.delete("/delete/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mensagem(item_id: uuid.UUID):
    try:
        db_response = supabase.table("mensagemaluno").delete().eq('id_mensagem', str(item_id)).execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail=f"Item com ID '{item_id}' não encotrado.")

        return
    except Exception as e:
        raise  HTTPException(status_code=500, detail=str(e))
