# Usar uma imagem Python oficial como base
FROM python:3.11-slim

# Diretório de trabalho dentro do container
WORKDIR /app

# Instalar dependências do sistema (opcional mas recomendado)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante da aplicação
COPY . .

# Expor a porta que o Uvicorn vai rodar
EXPOSE 8000

# Comando para rodar o Uvicorn
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
