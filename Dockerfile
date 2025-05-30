# Imagem base do Python
FROM python:3.13-slim

# Diretório de trabalho no container
WORKDIR /code

# Copia o arquivo de dependências
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia todos os arquivos da aplicação
COPY . .

# Comando para iniciar a aplicação
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
