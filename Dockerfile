# Zadanie 1: obraz z pipeline'em z lab. 3 (data_prep -> train -> evaluate)

# --- Etap 1: instalacja zależności narzędziem uv do osobnego venv ---
FROM python:3.11-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.11.14 /uv /bin/uv
RUN uv venv /opt/venv
# Najpierw sam requirements.txt: warstwa z bibliotekami trafia do cache
# i nie jest przebudowywana przy zmianach w kodzie
COPY requirements.txt .
RUN uv pip install --python /opt/venv/bin/python --no-cache -r requirements.txt

# --- Etap 2: lekki obraz końcowy (bez uv i plików pośrednich) ---
FROM python:3.11-slim
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
WORKDIR /app
# Tylko to, co potrzebne do uruchomienia pipeline'u i testów
COPY src/data_prep.py src/train.py src/evaluate.py src/
COPY .env.example pytest.ini ./
COPY tests/ tests/
CMD ["python", "src/train.py"]
