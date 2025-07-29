# backend/Dockerfile

# --- 1. Aşama: Builder (Bağımlılıkları Yükleme) ---
FROM python:3.13-slim as builder

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

RUN pip install poetry
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --only main

# --- 2. Aşama: Final (Uygulama İmajı) ---
FROM python:3.13-slim

WORKDIR /app

# Kütüphaneleri kopyala
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
# DÜZELTME: Çalıştırılabilir komutları (uvicorn gibi) kopyala
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --from=builder /app/pyproject.toml /app/pyproject.toml
COPY --from=builder /app/poetry.lock /app/poetry.lock

# Uygulama kodunun tamamını kopyala
COPY . .

# Uygulamanın çalışacağı portu dışarıya aç
EXPOSE 8000

# Konteyner çalıştığında uygulamayı başlatan komut
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]