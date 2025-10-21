from fastapi import APIRouter, UploadFile, File, HTTPException, status
import os
import shutil



router = APIRouter(
    prefix="/documentos",
    tags=["Documentos"]
)


# Caminho para a pasta que o seu script 'watcher' está monitorando
WATCH_FOLDER_PATH ="D:/APS/api_gemini/connectors/teams_mock_files"


# Garante que a pasta de destino exista ao iniciar a API
os.makedirs(WATCH_FOLDER_PATH, exist_ok=True)

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_documento(file: UploadFile = File(...)):

    # Validação básica do tipo de arquivo (opcional, mas recomendado)
    allowed_content_types = [
        "application/pdf",  # .pdf
        "text/plain",       # .txt
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # .docx
        "application/msword" # .doc
    ]
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de arquivo '{file.content_type}' não suportado. Use PDF, TXT ou DOCX."
        )

    try:
        # Caminho completo onde o arquivo será salvo
        destination_path = os.path.join(WATCH_FOLDER_PATH, file.filename)

        print(f"Recebendo arquivo: {file.filename}")
        print(f"Salvando em: {os.path.abspath(destination_path)}")

        # Salva o arquivo no disco de forma eficiente
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "message": f"Arquivo '{file.filename}' recebido e salvo para processamento.",
            "filename": file.filename,
            "content_type": file.content_type
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao salvar o arquivo: {e}"
        )
    finally:
        # Fecha o arquivo para liberar recursos
        await file.close()

