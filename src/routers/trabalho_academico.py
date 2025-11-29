from typing import List
from datetime import date
from fastapi import APIRouter, HTTPException, status, Depends
from ..supabase_client import supabase
from ..schemas.sch_trabalho_academico import (
    TrabalhoAcademicoCreate,
    TrabalhoAcademico,
    TrabalhoAcademicoUpdate,
    TipoTrabalhoEnum,
)
from ..dependencies import require_admin_or_coordenador
import uuid

# --- ROUTER TRABALHO ACADÊMICO ---

router = APIRouter(
    prefix="/trabalho_academico",
    tags=["Trabalho Acadêmico"],
)


### ENDPOINT PARA CADASTRAR TRABALHO ACADÊMICO ###
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TrabalhoAcademico)
def create_trabalho_academico(trabalho_data: TrabalhoAcademicoCreate):
    try:
        payload = trabalho_data.model_dump()

        # Converte campos de data/uuid/enum para string onde necessário
        for key, value in payload.items():
            if isinstance(value, (date, uuid.UUID)):
                payload[key] = str(value)
            elif isinstance(value, TipoTrabalhoEnum):
                payload[key] = value.value  # Converte Enum para string

        response = supabase.table("trabalho_academico").insert(payload).execute()

        if not response.data:
            raise HTTPException(
                status_code=500, detail="Erro ao criar o trabalho acadêmico."
            )

        return response.data[0]
    except Exception as e:
        if "violates foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail="Curso, disciplina ou orientador informado não foi encontrado.",
            )
        raise HTTPException(status_code=400, detail=str(e))


### ENDPOINT PARA BUSCAR TRABALHO POR ID ###
@router.get("/{trabalho_id}", response_model=TrabalhoAcademico)
def get_trabalho_academico_by_id(trabalho_id: uuid.UUID):
    try:
        response = (
            supabase.table("trabalho_academico")
            .select("*")
            .eq("id_trabalho", str(trabalho_id))
            .single()
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404, detail="Trabalho acadêmico não encontrado."
            )

        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


### ENDPOINT PARA LISTAR TRABALHOS POR CURSO ###
@router.get("/curso/{curso_id}", response_model=List[TrabalhoAcademico])
def get_trabalhos_por_curso(curso_id: uuid.UUID):
    try:
        response = (
            supabase.table("trabalho_academico")
            .select("*")
            .eq("id_curso", str(curso_id))
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


### ENDPOINT PARA LISTAR TRABALHOS POR DISCIPLINA ###
@router.get("/disciplina/{disciplina_id}", response_model=List[TrabalhoAcademico])
def get_trabalhos_por_disciplina(disciplina_id: uuid.UUID):
    try:
        response = (
            supabase.table("trabalho_academico")
            .select("*")
            .eq("id_disciplina", str(disciplina_id))
            .execute()
        )
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


### ENDPOINT PARA ATUALIZAR TRABALHO POR ID ###
@router.put("/update/{trabalho_id}", response_model=TrabalhoAcademico)
def update_trabalho_academico(trabalho_id: uuid.UUID, trabalho_update_data: TrabalhoAcademicoUpdate):
    try:
        update_payload = trabalho_update_data.model_dump(exclude_unset=True)

        if not update_payload:
            raise HTTPException(
                status_code=400, detail="Nenhum dado fornecido para atualização."
            )

        for key, value in update_payload.items():
            if isinstance(value, (date, uuid.UUID)):
                update_payload[key] = str(value)
            elif isinstance(value, TipoTrabalhoEnum):
                update_payload[key] = value.value  # Converte Enum para string

        response = (
            supabase.table("trabalho_academico")
            .update(update_payload)
            .eq("id_trabalho", str(trabalho_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404, detail="Trabalho acadêmico não encontrado."
            )

        return response.data[0]
    except Exception as e:
        if "violates foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail="Curso, disciplina ou orientador informado não foi encontrado.",
            )
        raise HTTPException(status_code=500, detail=str(e))


### ENDPOINT PARA DELETAR TRABALHO POR ID ###
@router.delete("/delete/{trabalho_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trabalho_academico(
    trabalho_id: uuid.UUID,
    current_user: dict = Depends(require_admin_or_coordenador),
):
    try:
        response = (
            supabase.table("trabalho_academico")
            .delete()
            .eq("id_trabalho", str(trabalho_id))
            .execute()
        )

        if not response.data:
            raise HTTPException(
                status_code=404, detail="Trabalho acadêmico não encontrado."
            )

        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



