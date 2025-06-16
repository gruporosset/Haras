FROM --platform=linux/amd64 python:3.12-bookworm

# Instalar dependências
RUN apt-get update && apt-get install -y \
    unzip \
    libaio1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Instalar o Oracle Instant Client 19.3 e as ferramentas
RUN mkdir -p /opt/oracle && \
    cd /opt/oracle && \
    curl -O https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-basic-linux.x64-19.23.0.0.0dbru.zip && \
    unzip instantclient-basic-linux.x64-19.23.0.0.0dbru.zip && \
    rm instantclient-basic-linux.x64-19.23.0.0.0dbru.zip 

# Instalar o Oracle Instant Client 19.3 e as ferramentas
ENV LD_LIBRARY_PATH /opt/oracle/instantclient_19_23
ENV PATH="/opt/oracle/instantclient_19_23:${PATH}"

# Diretório de trabalho
WORKDIR /usr/app

# arquivos de requisitos e instalacao das dependências
COPY requirements.txt .
RUN pip3.12 install --no-cache-dir -r requirements.txt

# Copiar o projeto para o contêiner
COPY . .


EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
