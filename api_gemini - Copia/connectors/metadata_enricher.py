import time
import os
import json
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURAÇÃO ---
WATCH_FOLDER = os.path.join('connectors', 'ia_processed_files')  # Monitora a pasta de saída da IA
API_FASTAPI_URL = "http://localhost:5000"


def get_id_disciplina_por_nome(nome_disciplina: str) -> str | None:
    """Busca o UUID de uma disciplina na API FastAPI usando seu nome."""
    print(f"   [Busca] 1.5. Procurando ID para a disciplina '{nome_disciplina}'...")
    try:
        response = requests.get(f"{API_FASTAPI_URL}/disciplina/nome/{nome_disciplina}")
        response.raise_for_status()
        id_disciplina = response.json().get("id_disciplina")
        if id_disciplina:
            print(f"   [Busca] 1.6. ID encontrado: {id_disciplina}")
            return id_disciplina
        return None
    except requests.exceptions.RequestException:
        print(f"   [ERRO Busca] Disciplina '{nome_disciplina}' não encontrada na API.")
        return None

## FUNÇÃO PARA POSTA A RESOLUÇÃO PARA O BASE DE CONHECIMENTO ##
def salvar_na_base_conhecimento(payload: dict) -> bool:
    print(f"   [API] 3. Enviando payload final para a API FastAPI...")
    try:
        response = requests.post(f"{API_FASTAPI_URL}/baseconhecimento/", json=payload)
        response.raise_for_status()
        print(f"   [API] 3.1. Dados salvos com sucesso no Supabase! (ID: {response.json().get('id_conhecimento')})")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   [ERRO API] Falha ao salvar no Supabase: {e}")
        return False


class NewJsonHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.json'):
            return
        time.sleep(2)

        json_path = event.src_path
        print(f"\n✔️  [ETAPA 2] Novo arquivo JSON detectado: {os.path.basename(json_path)}")

        try:
            # 1. Ler o JSON processado pela IA
            with open(json_path, 'r', encoding='utf-8') as f:
                dados_ia = json.load(f)

            nome_arquivo_origem = dados_ia.get('nome_arquivo_origem')
            if not nome_arquivo_origem:
                print("   [ERRO] JSON inválido, sem 'nome_arquivo_origem'.")
                return

            # 2. Extrair metadados do nome do arquivo
            # Convenção: DISCIPLINA-CATEGORIA-NOME.ext
            partes_nome = os.path.splitext(nome_arquivo_origem)[0].split('-')
            if len(partes_nome) < 2:
                print(f"   [ERRO] Nome do arquivo '{nome_arquivo_origem}' fora do padrão. Usando valores padrão.")
                nome_disciplina_extraido = "desconhecida"
                categoria_extraida = "Outros"
            else:
                nome_disciplina_extraido = partes_nome[0]
                categoria_extraida = partes_nome[1] if len(partes_nome) > 1 else "Geral"

            # 3. Buscar ID da disciplina
            id_disciplina = get_id_disciplina_por_nome(nome_disciplina_extraido)
            if not id_disciplina:
                print("   [AVISO] ID da disciplina não encontrado. Será salvo como nulo.")

            # 4. Montar o payload final
            payload_final = {
                "nome_arquivo_origem": nome_arquivo_origem,
                "conteudo_processado": dados_ia.get("resumo"),
                "palavras_chave": dados_ia.get("palavras_chave"),
                "categoria": categoria_extraida.replace("_", " "),
                "status": "publicado",
                "id_disciplina": id_disciplina
            }

            # 5. Salvar no banco de dados
            sucesso = salvar_na_base_conhecimento(payload_final)

            if sucesso:
                print(f"✅ [ETAPA 2] Processamento completo para '{nome_arquivo_origem}'.")
                os.remove(json_path)  # Limpa o arquivo JSON após o sucesso
                print(f"   [Limpeza] Arquivo temporário '{os.path.basename(json_path)}' removido.")
            else:
                print(
                    f"❌ [ETAPA 2] Falha no processamento de '{nome_arquivo_origem}'. O arquivo JSON será mantido para nova tentativa.")

        except Exception as e:
            print(f"🚨 Erro inesperado na ETAPA 2: {e}")


if __name__ == "__main__":
    print("======================================================")
    print("🤖 ETAPA 2 - ENRIQUECEDOR DE METADADOS INICIADO 🤖")
    print(f"Monitorando a pasta de JSONs: '{os.path.abspath(WATCH_FOLDER)}'")
    print("======================================================")

    event_handler = NewJsonHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("\n👋 Enriquecedor de metadados encerrado.")

