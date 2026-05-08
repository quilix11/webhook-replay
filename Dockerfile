FROM python:3.13-slim

WORKDIR /webhook_replay

RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction

COPY alembic.ini ./alembic.ini
COPY migrations ./migrations

COPY src ./src

CMD alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000