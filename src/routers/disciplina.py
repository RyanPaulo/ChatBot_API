from typing import List
from ..schemas.sch_cronograma import Cronograma
from fastapi import APIRouter, HTTPException, status, Depends
from ..supabase_client import supabase
from ..schemas.sch_disciplina import DisciplinaCreate, Disciplina, DisciplinaUpdate, DisciplinaEmenta
# from ..dependencies import 
import uuid

# --- ROUTER DISCIPLINA ---

router = APIRouter(
    prefix="/disciplinas",
    tags=["Disciplina"]
)

### ENDPOINT PARA CASDATRAR DISCIPLINAS #####
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Disciplina)
def create_disciplina(disciplina_data: DisciplinaCreate):
    try:
        disciplina_payload = disciplina_data.model_dump()

        # disciplina_payload['id_professor'] = str(disciplina_payload['id_professor'])

        db_response = supabase.table("disciplina").insert(disciplina_payload).execute()

        if not db_response.data:
            raise HTTPException(status_code=500, detail="Erro ao cadastrar a disciplina")

        return db_response.data[0]

    except Exception as e:
        if "violates foreig key constraint" in str(e).lower():
            raise HTTPException(status_code=404, datail=f"O professor com ID '{disciplina_data.id_professor}' não foi encontrado.")
        raise HTTPException(status_code=400, detail=str(e))

##### ENDPOINT PARA CONSULTAR AS DISCIPLINAS USANDO O ID ####
@router.get("/get_diciplina_id/{disciplina}", response_model=Disciplina)
def get_disciplina_detalhado(disciplina_id: uuid.UUID):
    try:
        db_response = supabase.table("disciplina").select(
            """
            *,
            professordisciplina!left(
                professor!inner(nome_professor, sobrenome_professor)
            ),
            cronograma!left(tipo_aula)
            """
        ).eq(
            'id_disciplina', str(disciplina_id)
        ).single().execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail="Disiciplina não encontrada.")


        data = db_response.data

        # 1. Processar os professores
        professores_list = []
        # A resposta pode não conter a chave se não houver relação
        if data.get('professordisciplina'):
            for item in data['professordisciplina']:
                if item and item.get('professor'):  # Checagem dupla de segurança
                    professores_list.append(item['professor'])
        data['professores'] = professores_list
        if 'professordisciplina' in data:
            del data['professordisciplina']

        # 2. Processar o tipo de aula
        # A resposta pode não conter a chave se não houver relação
        if data.get('cronograma') and data['cronograma']:
            data['tipo_aula'] = data['cronograma'][0]['tipo_aula']
        else:
            data['tipo_aula'] = None
        if 'cronograma' in data:
            del data['cronograma']


        return Disciplina.model_validate(data)

        # return db_response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA RETORNAR O CONTEUDO DA EMENTA ###
@router.get("/get_ementa/{disciplina_id}", response_model=DisciplinaEmenta)
def get_ementa_da_disciplina(disciplina_id: uuid.UUID):
    try:
        # seleciona apenas a coluna 'ementa' da tabela 'Disciplina'
        db_response = supabase.table("disciplina").select(
            "ementa"
        ).eq(
            'id_disciplina', str(disciplina_id)
        ).single().execute()


        if not db_response.data:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada.")

        return db_response.data

    except Exception as e:
        if "JSON object requested, multiple (or no) rows returned" in str(e):
             raise HTTPException(status_code=404, detail="Disciplina não encontrada.")
        raise HTTPException(status_code=500, detail=str(e))

#### ENDPOINT PARA BUSCAR O CRONOGRAMA DE UMA DISCIPLINA PELO NOME ####
@router.get("/get_diciplina_nome/{nome_disciplina}/cronograma", response_model=List[Cronograma]) #tags=["disciplina"]
def get_cronograma_por_disciplina(nome_disciplina: str):
    try:
        disciplina_response = supabase.table("disciplina").select("id_disciplina").ilike("nome_disciplina", f"%{nome_disciplina}%").execute()

        if not disciplina_response.data:
            raise HTTPException(status_code=404, detail=f"Disciplina '{nome_disciplina}' não encontrada.")

        disciplina_id = disciplina_response.data[0]['id_disciplina']

        cronograma_response = supabase.table("cronograma").select("*").eq('id_disciplina', disciplina_id).execute()

        if not cronograma_response.data:
            raise HTTPException(status_code=404, detail=f"Nenhum cronograma encontrado para a disciplina '{nome_disciplina}'.")

        return cronograma_response.data


    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        # Captura outras exceções genéricas
        raise HTTPException(status_code=500, detail=str(e ))

### ENDPOINT PARA LISTAR TODOS OS DISCIPLINA CADASTRADOS NO BD ###
@router.get("/lista_disciplina/", response_model=list[Disciplina])
def get_all_disciplina():
    try:
        response = supabase.table("disciplina").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA ATUALIZAR AVALIACAO ###
@router.put("/update/{disciplina_id}", response_model=Disciplina)
def update_disciplina(disciplina_id: uuid.UUID, disciplina_data: DisciplinaUpdate):
    try:
        update_payload = disciplina_data.model_dump(exclude_unset=True)

        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualização")

        if 'id_professor' in update_payload:
            update_payload['id_professor'] = str(update_payload['id_professor'])

        response = supabase.table('disciplina').update(update_payload).eq('id_disciplina', str(disciplina_id)).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Disciplina não encontrada para atualização.")

        return response.data[0]
    except Exception as e:
        if "violates foreig key constraint" in str(e).lower() and "fk_professor" in str(e).lower():
            raise HTTPException(status_code=404,
                                detail=f"O novo professor com id '{disciplina_data.id_professor}' não foi encontrado.")

        raise HTTPException(status_code=500, detail=str(e))

### ENDPOINT PARA DELETAR AVALIACAO ###
@router.delete("/delete/{disciplina_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disciplina(disciplina_id: uuid.UUID):
    try:
        db_response = supabase.table('disciplina').delete().eq('id_disciplina', str(disciplina_id)).execute()

        if not db_response.data:
            raise HTTPException(status_code=404, detail="Avaliação nãoi encotrado para deletar")

        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

