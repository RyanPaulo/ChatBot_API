# test_supabase_connection.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv

print("Iniciando teste de conexão com o Supabase...")

# 1. Carregar as variáveis de ambiente do arquivo .env
try:
    load_dotenv()
    print("-> Arquivo .env carregado com sucesso.")
except Exception as e:
    print(f"[ERRO] Não foi possível carregar o arquivo .env: {e}")
    exit()  # Sai do script se não conseguir carregar as credenciais

# 2. Obter as credenciais
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

# Verifica se as credenciais foram carregadas
if not supabase_url or not supabase_key:
    print("[ERRO] As variáveis SUPABASE_URL e/ou SUPABASE_KEY não foram encontradas no .env.")
    print("Verifique se o arquivo .env está na pasta raiz e contém as variáveis corretas.")
    exit()

print(f"-> URL do Supabase encontrada: ...{supabase_url[-10:]}")  # Mostra apenas o final da URL por segurança

# 3. Tentar criar o cliente Supabase
try:
    supabase: Client = create_client(supabase_url, supabase_key)
    print("-> Cliente Supabase criado com sucesso.")
except Exception as e:
    print(f"[ERRO] Falha ao criar o cliente Supabase: {e}")
    exit()

# 4. Tentar executar uma consulta no banco de dados
try:
    print("-> Tentando consultar a tabela 'aluno'...")
    # Tenta buscar apenas o campo 'id' do primeiro aluno encontrado
    response = supabase.table('aluno').select('id').limit(1).execute()

    # O Supabase retorna uma resposta mesmo que a tabela esteja vazia.
    # O importante é que a chamada não gere uma exceção.
    print("\n" + "=" * 40)
    print("  CONEXÃO BEM-SUCEDIDA! ✅")
    print("=" * 40)
    print("Sua API conseguiu se conectar e autenticar com o Supabase.")
    print("Seus dados de conexão no arquivo .env estão corretos.")

    # Opcional: mostrar os dados se houver algum aluno na tabela
    if response.data:
        print("\nDados de teste recebidos do banco:")
        print(response.data)
    else:
        print("\nNota: A consulta foi bem-sucedida, mas a tabela 'aluno' está vazia.")

except Exception as e:
    print("\n" + "=" * 40)
    print("  FALHA NA CONEXÃO! ❌")
    print("=" * 40)
    print("O cliente foi criado, mas a consulta ao banco de dados falhou.")
    print("Possíveis causas:")
    print("1. A 'key' do Supabase pode estar errada (verifique se é a 'anon key' ou 'service_role key').")
    print("2. Pode haver um problema de rede ou firewall bloqueando a conexão.")
    print("3. A tabela 'aluno' pode não existir no seu banco de dados.")
    print("\nDetalhes do erro original:")
    print(e)

