FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
ENV CHATIFY_RERANK_MODEL_DIR=/app/chatify/models/rerank
EXPOSE 8080
CMD ["sh", "-c", "python -m chatify run ${APP:-apps/minimal/app.yaml} --host 0.0.0.0 --port ${PORT:-8080}"]
