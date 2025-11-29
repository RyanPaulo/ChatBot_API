from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form, Depends
import os
import shutil
import json
import uuid
import re
import unicodedata
import google.generativeai as genai
from ..config import settings
from ..supabase_client import supabase
# from ..dependencies import 

router = APIRouter(
    prefix="/documentos",
    tags=["Documentos"],
)


# Pasta temporária para processar arquivos antes de enviar ao Supabase Storage
TEMP_FOLDER_PATH = "D:/APS/api_gemini/connectors/teams_mock_files"

# Garante que a pasta temporária exista
os.makedirs(TEMP_FOLDER_PATH, exist_ok=True)

# Nome do bucket no Supabase Storage
BUCKET_NAME = "documentos"


# Configura o Gemini (reutiliza mesma chave do projeto)
genai.configure(api_key=settings.GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")


def _extrair_disciplina_e_categoria(nome_arquivo: str) -> tuple[str, str]:
    """
    Replica a lógica do metadata_enricher:
    DISCIPLINA-CATEGORIA-NOME.ext
    """
    base_name = os.path.splitext(nome_arquivo)[0]
    partes = base_name.split("-")
    if len(partes) < 2:
        print(
            f"   [ERRO] Nome do arquivo '{nome_arquivo}' fora do padrão. Usando valores padrão."
        )
        return "desconhecida", "Outros"

    nome_disciplina = partes[0]
    categoria = partes[1] if len(partes) > 1 else "Geral"
    return nome_disciplina, categoria.replace("_", " ")


def _buscar_id_disciplina_por_nome(nome_disciplina: str) -> str | None:
    """
    Busca o UUID de uma disciplina diretamente no Supabase pela coluna nome_disciplina.
    """
    print(
        f"   [Busca] Procurando ID para a disciplina '{nome_disciplina}' na tabela 'disciplina'..."
    )
    try:
        # Usamos limit(1) em vez de .single() para evitar erro quando não há linhas
        response = (
            supabase.table("disciplina")
            .select("id_disciplina")
            .eq("nome_disciplina", nome_disciplina)
            .limit(1)
            .execute()
        )

        rows = response.data or []
        if rows:
            disciplina_id = rows[0].get("id_disciplina")
            if disciplina_id:
                print(f"   [Busca] ID encontrado: {disciplina_id}")
                return disciplina_id

        print("   [Busca] Nenhuma disciplina encontrada com esse nome (isso é esperado se for 'desconhecida').")
        return None
    except Exception as e:
        print(f"   [ERRO Busca] Erro ao buscar disciplina: {e}")
        return None


def _normalizar_nome_arquivo(nome_arquivo: str) -> str:
    """
    Normaliza o nome do arquivo para ser compatível com Supabase Storage.
    Remove acentos, espaços e caracteres especiais, mantendo apenas alfanuméricos, hífens e underscores.
    """
    # Separa nome e extensão
    nome_base, extensao = os.path.splitext(nome_arquivo)
    
    # Remove acentos e normaliza para ASCII
    nome_normalizado = unicodedata.normalize('NFKD', nome_base)
    nome_normalizado = ''.join(c for c in nome_normalizado if not unicodedata.combining(c))
    
    # Remove caracteres especiais, mantém apenas alfanuméricos, hífens e underscores
    nome_normalizado = re.sub(r'[^a-zA-Z0-9_-]', '_', nome_normalizado)
    
    # Remove underscores múltiplos
    nome_normalizado = re.sub(r'_+', '_', nome_normalizado)
    
    # Remove underscores no início e fim
    nome_normalizado = nome_normalizado.strip('_')
    
    # Se ficar vazio, usa um nome padrão
    if not nome_normalizado:
        nome_normalizado = "documento"
    
    # Adiciona UUID para evitar conflitos e retorna com extensão
    nome_final = f"{nome_normalizado}_{uuid.uuid4().hex[:8]}{extensao}"
    
    return nome_final


def _upload_para_supabase_storage(caminho_arquivo: str, nome_arquivo: str) -> str:
    """
    Faz upload do arquivo para o Supabase Storage usando um nome normalizado.
    Retorna a URL pública.
    """
    print(f"   [Storage] 1. Fazendo upload do arquivo para o bucket '{BUCKET_NAME}'...")
    
    try:
        # Lê o arquivo em bytes
        with open(caminho_arquivo, "rb") as f:
            file_data = f.read()
        
        # Normaliza o nome do arquivo para ser compatível com Supabase Storage
        nome_arquivo_normalizado = _normalizar_nome_arquivo(nome_arquivo)
        
        print(f"   [Storage] Nome original: {nome_arquivo}")
        print(f"   [Storage] Nome normalizado: {nome_arquivo_normalizado}")
        
        # Faz upload para o bucket usando o nome normalizado
        # Usa a service key que deve contornar RLS
        try:
            response = supabase.storage.from_(BUCKET_NAME).upload(
                path=nome_arquivo_normalizado,
                file=file_data,
                file_options={
                    "content-type": "application/octet-stream",
                    "upsert": "true",
                    "x-upsert": "true"  # Garante upsert
                }
            )
        except Exception as upload_error:
            # Se der erro de RLS, tenta criar o bucket primeiro (se não existir)
            error_str = str(upload_error)
            if "row-level security" in error_str.lower() or "403" in error_str or "Unauthorized" in error_str:
                print(f"   [Storage] Erro de RLS detectado. Verificando configuração do bucket...")
                print(f"   [Storage] AVISO: O bucket '{BUCKET_NAME}' pode ter RLS habilitado.")
                print(f"   [Storage] Solução: No Supabase Dashboard, vá em Storage > {BUCKET_NAME} > Policies")
                print(f"   [Storage] e desabilite RLS ou crie uma política que permita uploads com service key.")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Erro de permissão no Supabase Storage. O bucket '{BUCKET_NAME}' tem RLS habilitado. "
                           f"Desabilite RLS no bucket ou configure políticas adequadas no Supabase Dashboard. "
                           f"Erro original: {error_str}",
                )
            raise
        
        # Obtém a URL pública do arquivo
        # get_public_url retorna um dicionário com a chave 'publicUrl' ou a URL diretamente
        public_url_response = supabase.storage.from_(BUCKET_NAME).get_public_url(nome_arquivo_normalizado)
        
        # Se for um dicionário, extrai a URL; se for string, usa diretamente
        if isinstance(public_url_response, dict):
            url_documento = public_url_response.get("publicUrl") or public_url_response.get("url") or str(public_url_response)
        else:
            url_documento = str(public_url_response)
        
        print(f"   [Storage] 2. Arquivo enviado com sucesso!")
        print(f"   [Storage] 3. URL pública: {url_documento}")
        
        return url_documento
        
    except Exception as e:
        print(f"   [ERRO Storage] Falha ao fazer upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer upload do arquivo para o Supabase Storage: {e}",
        )


def _processar_com_gemini(caminho_arquivo: str, content_type: str) -> dict:
    """
    Lê o arquivo e pede para o Gemini gerar:
    - resumo (conteudo_processado)
    - palavras_chave (lista de strings)

    Retorna um dicionário já pronto para ser usado.
    """
    print("   [Gemini] 1. Enviando documento para o Gemini para processamento...")

    # Faz upload do arquivo para o Gemini como input multimodal
    try:
        with open(caminho_arquivo, "rb") as f:
            uploaded_file = genai.upload_file(f, mime_type=content_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao enviar arquivo para o Gemini: {e}",
        )

    prompt = """
Você é um assistente acadêmico.
Leia o documento fornecido e responda ESTRITAMENTE em JSON válido, sem comentários nem texto extra.
O formato DEVE ser exatamente:
{
  "resumo": "um resumo em português, com 3 a 8 frases, bem objetivas.",
  "palavras_chave": ["keyword1", "keyword2", "..."]
}

Regras importantes:
- Não inclua nenhum outro campo além de "resumo" e "palavras_chave".
- "palavras_chave" deve ser uma lista de strings curtas (1 a 3 palavras cada).
"""

    try:
        response = gemini_model.generate_content([prompt, uploaded_file])
        raw_text = response.text.strip()
        print(f"   [Gemini] 2. Resposta bruta do modelo:\n{raw_text[:400]}...")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao comunicar com a API do Gemini: {e}",
        )

    # Às vezes o modelo devolve ```json ... ```, então limpamos isso
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        # remove possível prefixo "json\n"
        if raw_text.lower().startswith("json"):
            raw_text = raw_text[4:]

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"   [Gemini] 3. ERRO ao fazer parse do JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Falha ao interpretar resposta do Gemini como JSON: {e}",
        )

    resumo = data.get("resumo", "").strip()
    palavras_chave = data.get("palavras_chave") or []

    if not isinstance(palavras_chave, list):
        palavras_chave = [str(palavras_chave)]

    print("   [Gemini] 4. Resumo gerado:")
    print(f"       {resumo[:300]}...")
    print("   [Gemini] 5. Palavras-chave extraídas:")
    print(f"       {palavras_chave}")

    return {
        "resumo": resumo,
        "palavras_chave": palavras_chave,
    }


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_documento(
    file: UploadFile = File(...),
    nome_disciplina: str = Form(..., description="Nome exato da disciplina cadastrada"),
):
    # Validação básica do tipo de arquivo (opcional, mas recomendado)
    allowed_content_types = [
        "application/pdf",  # .pdf
        "text/plain",  # .txt
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/msword",  # .doc
    ]
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de arquivo '{file.content_type}' não suportado. Use PDF, TXT ou DOCX.",
        )

    try:
        # Caminho temporário onde o arquivo será salvo para processamento
        destination_path = os.path.join(TEMP_FOLDER_PATH, file.filename)

        print(f"Recebendo arquivo: {file.filename}")
        print(f"Salvando temporariamente em: {os.path.abspath(destination_path)}")

        # Salva o arquivo temporariamente no disco para processamento
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 1) Usar o nome da disciplina informado pelo usuário
        disciplina_id = _buscar_id_disciplina_por_nome(nome_disciplina.strip())

        # 2) Processar o conteúdo com o Gemini (resumo + palavras-chave)
        resultado_gemini = _processar_com_gemini(destination_path, file.content_type)

        # 2.1) Deixar a "categoria" a cargo do Gemini:
        #      usamos a primeira palavra-chave como categoria principal, se existir.
        palavras_chave = resultado_gemini["palavras_chave"]
        categoria = palavras_chave[0] if palavras_chave else "Geral"

        # 3) Fazer upload do arquivo para o Supabase Storage
        url_documento = _upload_para_supabase_storage(destination_path, file.filename)

        # 4) Remover arquivo temporário após upload bem-sucedido
        try:
            os.remove(destination_path)
            print(f"   [Limpeza] Arquivo temporário removido: {file.filename}")
        except Exception as e:
            print(f"   [AVISO] Não foi possível remover arquivo temporário: {e}")

        # 5) Montar payload para a tabela baseconhecimento
        payload_base = {
            "nome_arquivo_origem": file.filename,
            "conteudo_processado": resultado_gemini["resumo"],
            "palavra_chave": json.dumps(palavras_chave),
            "categoria": categoria,
            "status": "publicado",
            "id_disciplina": str(disciplina_id) if disciplina_id else None,
            "url_documento": url_documento,
        }

        print("   [API] 6. Salvando conteúdo na tabela 'baseconhecimento'...")
        db_response = (
            supabase.table("baseconhecimento").insert(payload_base).execute()
        )

        if not db_response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao salvar na base de conhecimento.",
            )

        registro = db_response.data[0]
        print(
            f"   [API] 7. Salvo com sucesso na base de conhecimento (id_conhecimento={registro.get('id_conhecimento')})."
        )

        return {
            "message": f"Arquivo '{file.filename}' recebido, processado pelo Gemini, enviado para o Supabase Storage e salvo na base de conhecimento.",
            "filename": file.filename,
            "content_type": file.content_type,
            "url_documento": url_documento,
            "base_conhecimento": {
                "id_conhecimento": registro.get("id_conhecimento"),
                "categoria": categoria,
                "id_disciplina": disciplina_id,
                "resumo": resultado_gemini["resumo"],
                "palavra_chave": resultado_gemini["palavras_chave"],
                "url_documento": url_documento,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao processar o arquivo: {e}",
        )
    finally:
        # Fecha o arquivo para liberar recursos
        await file.close()

