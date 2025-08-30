from fastapi import APIRouter, HTTPException, status
from src.supabase_client import supabase
from src.schemas.sch_coordenador import CoordenadorCreate, Coordenador, CoordenadorUpdate

# --- ROUTER COORDENADOR ---

router = APIRouter(
    prefix="/coordenador",
    tags=["Coordenador"]
)

### ENDPOINT PARA CADASTRAR COORDENADOR ###
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Coordenador)
def create_coordenador(coordenador_data: CoordenadorCreate):
    try:

        auth_response = supabase.auth.sign_up({
            "email": coordenador_data.email_institucional,
            "password": coordenador_data.password
        })
        user_id = auth_response.user.id


        coordenador_profile_data = coordenador_data.model_dump(exclude={"password"})
        coordenador_profile_data["id"] = user_id


        db_response = supabase.table("coordenador").insert(coordenador_profile_data).execute()


        if not db_response.data:
            raise HTTPException(status_code=500, detail="Erro ao salvar o perfil do coordenador")

        return db_response.data[0]

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


    # **** ENDPOINT PARA ATUALIZAR CADASTRO DO COORDENADOR ****

### ENDPOINT PARA ATUALIZAR COORDENADOR ###
@router.put("/{id}", response_model=Coordenador)
def update_coordenador(id: str, coordenador_update_data: CoordenadorUpdate):
    try:

        update_payload = coordenador_update_data.model_dump(exclude_unset=True)


        if not update_payload:
            raise HTTPException(status_code=400, detail="Nenhum dado fornecido para atualiuzação.")

        response = supabase.table('coordenador').update(update_payload).eq('id_funcional', id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Coordenador não encontrado para atualização")

        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


### ENDPOINR PARA DELETAR COORDENADOR ###
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coordenador(id: str):
    try:
        response = supabase.table('coordenador').delete().eq('id_funcional', id).execute()

        if not response.data:
            raise HTTPException(status_code=404, detail="Coordenador não encontrado para deletar")

        return

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
