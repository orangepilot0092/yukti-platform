FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- PRINCIPAL ENGINEER MOVE ---
# Pre-download the embedding model during the build.
# This bakes the 80MB model into the Docker image so we don't 
# have to download it from HuggingFace every time the container restarts.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY ./app /app/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
