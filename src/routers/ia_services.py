from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from ..config import settings

# Carrega a chave da API do Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

router = APIRouter(
    prefix="/ia",
    tags=["Serviços de IA"]
)

class GenerationRequest(BaseModel):
    pergunta: str
    contexto: str

@router.post("/gerar-resposta")
async def gerar_resposta_com_ia(request: GenerationRequest):
    """
    Recebe uma pergunta e um contexto, e usa o Gemini para gerar uma resposta
    baseada estritamente nesse contexto.
    """
    prompt = f"""
    Você é um assistente acadêmico. Sua tarefa é responder a pergunta do usuário de forma clara e objetiva,
    baseando-se exclusivamente no contexto fornecido abaixo. Não use nenhum conhecimento externo.
    Se a resposta não estiver no contexto, diga "Com base no material que tenho, não encontrei uma resposta para sua pergunta.".

    **Contexto:**
    ---
    {request.contexto}
    ---

    **Pergunta do Usuário:**
    {request.pergunta}

    **Resposta Concisa:**
    """
    try:
        response = gemini_model.generate_content(prompt)
        return {"resposta": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao comunicar com a API do Gemini: {e}")
