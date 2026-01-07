FROM python:3.11-slim

# Set working directory
WORKDIR /srv/guweb

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libmariadb-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy poetry files first for better caching
COPY pyproject.toml poetry.lock* /srv/guweb/

# Configure poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Copy application code
COPY . /srv/guweb

# Create necessary directories
RUN mkdir -p /srv/guweb/.data/avatars \
    /srv/guweb/.data/banners \
    /srv/guweb/.data/backgrounds

# Expose port
EXPOSE 8000

# Run with hypercorn for production
CMD ["python3.11", "-m", "hypercorn", "main:app", "--bind", "0.0.0.0:8000"]
