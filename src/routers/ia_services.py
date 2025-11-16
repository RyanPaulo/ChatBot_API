from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from ..config import settings
from ..supabase_client import supabase

# Carrega a chave da API do Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.0-flash')

router = APIRouter(
    prefix="/ia",
    tags=["Serviços de IA"],
)

class GenerationRequest(BaseModel):
    pergunta: str
    contexto: str | None = None

@router.post("/gerar-resposta")
async def gerar_resposta_com_ia(request: GenerationRequest):
    """
    Recebe uma pergunta, consulta a base de conhecimento no Supabase
    e usa o Gemini para gerar uma resposta baseada estritamente nesse contexto.
    """

    # 1) Buscar contexto na base de conhecimento via função RPC "buscar_conteudo"
    contexto_base = ""
    try:
        search_response = supabase.rpc(
            "buscar_conteudo", {"query": request.pergunta}
        ).execute()

        if search_response.data:
            # Usa apenas os primeiros N resultados para evitar prompt muito grande
            contextos = [
                item.get("conteudo_processado")
                or item.get("conteudo_original")
                or ""
                for item in search_response.data
            ]
            contexto_base = "\n\n---\n\n".join(contextos[:5])
    except Exception as e:
        # Em caso de erro na busca, apenas segue sem contexto da base
        contexto_base = ""

    # 2) Combinar contexto enviado pelo usuário (se existir) com o da base
    partes_contexto = []
    if request.contexto:
        partes_contexto.append(str(request.contexto))
    if contexto_base:
        partes_contexto.append(contexto_base)

    contexto_final = "\n\n---\n\n".join(partes_contexto) if partes_contexto else "NENHUM CONTEXTO DISPONÍVEL."

    # 3) Montar o prompt para o Gemini
    prompt = f"""
Você é um assistente acadêmico. Sua tarefa é responder à pergunta do usuário de forma clara, objetiva e pedagógica.
Baseie-se EXCLUSIVAMENTE no contexto fornecido abaixo (que vem da base de conhecimento do sistema).
Não use nenhum conhecimento externo ou invente informações.
Se a resposta não estiver claramente presentes no contexto, diga exatamente:
"Com base no material que tenho, não encontrei uma resposta para sua pergunta.".

================ CONTEXTO =================
{contexto_final}
===========================================

Pergunta do usuário: {request.pergunta}

Responda de forma concisa e bem estruturada:
"""

    try:
        response = gemini_model.generate_content(prompt)
        return {"resposta": response.text}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao comunicar com a API do Gemini: {e}",
        )

