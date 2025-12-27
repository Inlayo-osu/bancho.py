FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /srv/root

RUN apt update && apt install --no-install-recommends -y \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./
RUN pip install -U pip poetry==2.2.1
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

# NOTE: done last to avoid re-run of previous steps
COPY . .

# Create data directories
RUN mkdir -p .data/avatars .data/banners .data/backgrounds

EXPOSE 8000

# Run with hypercorn for production
CMD ["poetry", "run", "hypercorn", "main:app", "--bind", "0.0.0.0:8000"]
