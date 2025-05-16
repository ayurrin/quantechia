# Dockerfile
FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# JupyterLabのインストール
RUN pip install jupyterlab ipykernel

# コンテナ起動時にJupyterを実行するようにはせず、手動で実行できるように
CMD ["bash"]
