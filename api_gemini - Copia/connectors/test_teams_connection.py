import requests
import msal
import json

# --- CONFIGURE AQUI ---

TENANT_ID = "0d08fc28-286e-4be8-aed5-bd136743455e" # ID DE DIRETORIO (LOCATARIO)
CLIENT_ID = "d5f6e935-c514-4cb7-aee1-fe74adef8fad" # ID DE APLICATIVO(CLIENTE)
CLIENT_SECRET = "SDR8Q~w~16j~rgGLoRZVOfTF2rN4rIA6FGXgKc5N" # SEGREDO DE CLIENTE


TEAM_ID = "72f69038-aa2d-49a8-a2de-66471811d887&tenantId=d193e68c-e53f-4610-a66d-56ff300fec7a" # ID DA EQUIPE
CHANNEL_ID = "19%3ARsEhwHGYuOkrKzg_KJ1scvgvy40J_DznMro0wyOatjY1%40thread.tacv2" # ID DO CANAL
# --------------------

# URL de autoridade para o login da Microsoft
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

# Endpoint da API do Microsoft Graph para ler mensagens do canal

ENDPOINT = f"https://graph.microsoft.com/v1.0/teams/{TEAM_ID}/channels/{CHANNEL_ID}/messages"

# Escopo necessário para a API do Graph. '.default' usa as permissões que definimos no Azure.
SCOPE = ["https://graph.microsoft.com/.default"]

# 1. INICIAR O PROCESSO DE AUTENTICAÇÃO
# Cria uma instância do aplicativo cliente confidencial
app = msal.ConfidentialClientApplication(
    client_id=CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

# Tenta obter um token do cache. Se não houver, adquire um novo.
result = app.acquire_token_silent(scopes=SCOPE, account=None)

if not result:
    print("Cache de token não encontrado, adquirindo um novo token...")
    result = app.acquire_token_for_client(scopes=SCOPE)

# 2. FAZER A CHAMADA À API
if "access_token" in result:
    access_token = result['access_token']
    print("Token de acesso adquirido com sucesso!")

    # Monta o cabeçalho da requisição com o token
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Faz a requisição GET para a API do Graph
    response = requests.get(ENDPOINT, headers=headers)

    if response.status_code == 200:
        print("\nConexão bem-sucedida! As últimas mensagens do canal são:\n")
        messages = response.json().get('value', [])
        if not messages:
            print("Nenhuma mensagem encontrada no canal.")
        else:
            for message in messages[:5]:  # Mostra as 5 primeiras
                author = message.get('from', {}).get('user', {}).get('displayName', 'App/Bot')
                content = message.get('body', {}).get('content', '').strip()

                # O conteúdo vem em HTML, vamos simplificar para texto puro
                if "<" in content and ">" in content:
                    content = " (Conteúdo em HTML, pode incluir arquivos, imagens, etc.)"

                print(f"-> De: {author}")
                print(f"   Conteúdo: {content}\n")
                # Imprime a mensagem completa para análise
                # print(json.dumps(message, indent=2))

    else:
        print(f"\nErro ao acessar a API do Graph: {response.status_code}")
        print("Resposta do erro:", response.text)

else:
    print("Erro ao adquirir o token de acesso:")
    print(result.get("error"))
    print(result.get("error_description"))

