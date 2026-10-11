FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENV=railway \
    PROCESS=bot

# System deps for psycopg2, Pillow, lxml, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libffi-dev \
        libjpeg-dev \
        zlib1g-dev \
        libxml2-dev \
        libxslt1-dev \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/rowboat

# Install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir psycogreen gevent Flask peewee psycopg2-binary redis PyYAML click || true

# Try to install the original disco-py (may fail on modern Python; non-fatal)
RUN pip install --no-cache-dir \
    "git+https://github.com/b1naryth1ef/disco.git@530a79f1139a9e535df87f9e8823e60a57584c3d#egg=disco-py" \
    || pip install --no-cache-dir git+https://github.com/b1naryth1ef/disco.git || true

# Holster (used by the web panel)
RUN pip install --no-cache-dir git+https://github.com/b1naryth1ef/holster.git || true

COPY . .

# Entrypoint generates config.yaml from env vars then starts the chosen process
RUN chmod +x entrypoint.py
ENTRYPOINT ["python", "entrypoint.py"]
