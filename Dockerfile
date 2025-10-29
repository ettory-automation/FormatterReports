FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    FLASK_SECRET_KEY="flask_secret_key"
    # Altere o valor da ENV FLASK_SECRET_KEY!

RUN adduser --disabled-password --gecos "" formreports

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY app /app

USER formreports

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers=4", "--threads=2", "--timeout=120"]
