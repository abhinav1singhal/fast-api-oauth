
FROM python:3.10-slim

WORKDIR /usr/src/app

# Copy poetry.lock and pyproject.toml for Poetry
COPY poetry.lock pyproject.toml ./

# Install Poetry and project dependencies
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]