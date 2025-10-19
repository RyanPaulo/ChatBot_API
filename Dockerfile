# Dockerfile

# PASSO 1: Escolher a imagem base
# Usaremos uma imagem oficial do Python, que já vem com Python e pip.
# A tag '-slim' indica uma versão mais leve, ótima para produção.
FROM python:3.10-slim

# PASSO 2: Definir o diretório de trabalho dentro do contêiner
# Todos os comandos seguintes serão executados a partir deste diretório.
WORKDIR /api

# PASSO 3: Copiar o arquivo de dependências
# Copiamos primeiro para aproveitar o cache do Docker. Se este arquivo não mudar,
# o Docker não reinstalará as dependências toda vez.
COPY requirements.txt .

# PASSO 4: Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# PASSO 5: Copiar o resto do código do projeto para o contêiner
COPY . .

# PASSO 6: Expor a porta que a aplicação usa
# Nossa aplicação Flask roda na porta 5000.
EXPOSE 5005

# PASSO 7: Definir o comando para iniciar a aplicação
# Este é o comando que será executado quando o contêiner iniciar.
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5005", "--reload"]

