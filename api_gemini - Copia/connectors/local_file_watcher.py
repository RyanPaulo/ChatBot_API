# ==============================================================================
# SCRIPT: local_file_watcher.py (ETAPA 1 - PROCESSADOR DE IA)
# FUNÇÃO: Monitora a pasta de entrada, processa o conteúdo com Gemini e
#         salva o resultado em um arquivo JSON para a próxima etapa.
# AMBIENTE VIRTUAL: .venv_watcher
# ==============================================================================

import time
import os
import google.generativeai as genai
import json
import fitz
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURAÇÃO ---
load_dotenv()
WATCH_FOLDER = os.path.join('connectors', 'teams_mock_files')
OUTPUT_FOLDER = os.path.join('connectors', 'ia_processed_files')  # Nova pasta de saída!
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)


def processar_arquivo_com_ia(conteudo_arquivo: str) -> dict | None:
    """Envia o conteúdo para o Gemini e retorna o JSON com resumo e palavras-chave."""
    print("   [IA] 2. Enviando conteúdo para a API do Google Gemini...")
    prompt_template = f"""
    Sua tarefa é ler o texto a seguir e retornar as seguintes informações em formato JSON:
    1. Um resumo conciso do conteúdo principal (chave: "resumo").
    2. Uma lista de 5 a 7 palavras-chave ou termos técnicos importantes (chave: "palavras_chave").

    Texto para análise:
    ---
    {conteudo_arquivo}
    ---

    Retorne APENAS o objeto JSON, sem nenhum texto ou marcadores de código.
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt_template)
        resposta_json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
        dados_extraidos = json.loads(resposta_json_str)
        print("   [IA] 2.1. Resposta do Gemini recebida com sucesso.")
        return dados_extraidos
    except Exception as e:
        print(f"   [ERRO IA] Falha ao comunicar com a API do Gemini: {e}")
        return None


class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        time.sleep(2)

        file_path = event.src_path
        nome_arquivo_origem = os.path.basename(file_path)
        print(f"\n✔️  [ETAPA 1] Novo arquivo detectado: {nome_arquivo_origem}")

        conteudo = ""
        try:
            print("   [Leitura] 1. Lendo o conteúdo do arquivo...")
            # with open(file_path, 'r', encoding='utf-8') as f:
            #     conteudo = f.read()

            # Condições para quando o documento for .PDf
            if nome_arquivo_origem.lower().endswith('.pdf'):

                print(" -> Detectado arquivo PDF, Usando PyMuPDF para extrair texto.")
                with fitz.open(file_path) as doc:
                    for page in doc:
                        conteudo += page.get_text()
            else:
                # Para outros arquivos (txt, md, etc.), tente ler como texto simples
                print("      -> Lendo como arquivo de texto padrão (UTF-8).")
                with open(file_path, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

            # Se não foi possível extrair conteúdo, pare o processamento
            if not conteudo.strip():
                print("   [AVISO] Não foi possível extrair conteúdo textual do arquivo.")
                return



            dados_da_ia = processar_arquivo_com_ia(conteudo)

            if dados_da_ia:
                # Adiciona o nome do arquivo original aos dados da IA
                dados_da_ia['nome_arquivo_origem'] = nome_arquivo_origem

                # Salva o resultado em um novo arquivo JSON na pasta de saída
                output_filename = f"{os.path.splitext(nome_arquivo_origem)[0]}.json"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)

                with open(output_path, 'w', encoding='utf-8') as f_out:
                    json.dump(dados_da_ia, f_out, ensure_ascii=False, indent=4)

                print(f"   [Saída] 3. Resultado da IA salvo em: {output_path}")
                print(f"✅ [ETAPA 1] Processamento de IA concluído para '{nome_arquivo_origem}'.")
            else:
                print(f"❌ [ETAPA 1] Falha no processamento de IA para '{nome_arquivo_origem}'.")

        except Exception as e:
            print(f"🚨 Erro inesperado na ETAPA 1: {e}")


if __name__ == "__main__":
    if not GOOGLE_API_KEY:
        print("🚨 ERRO CRÍTICO: GOOGLE_API_KEY não encontrada no .env.")
    else:
        print("======================================================")
        print("🤖 ETAPA 1 - PROCESSADOR DE IA INICIADO 🤖")
        print(f"Monitorando a pasta de entrada: '{os.path.abspath(WATCH_FOLDER)}'")
        print("======================================================")

        event_handler = NewFileHandler()
        observer = Observer()
        observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
        observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
        print("\n👋 Processador de IA encerrado.")
