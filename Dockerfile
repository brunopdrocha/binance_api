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

# Define a variável de ambiente para a porta
ENV PORT=80

# Expõe a porta 80
EXPOSE 80

# Comando para rodar o app Flask diretamente
CMD ["python", "app.py"]