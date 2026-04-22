FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
# Install locked production dependencies for reproducible builds.
RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "main.py"]
