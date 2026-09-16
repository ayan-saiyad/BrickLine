FROM python:3.12.8-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN groupadd --system brickline && useradd --system --gid brickline --create-home brickline

WORKDIR /app
COPY pyproject.toml alembic.ini ./
COPY app ./app
COPY migrations ./migrations
COPY data ./data
RUN pip install --no-cache-dir .

USER brickline
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

