FROM python:3.11
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir poetry==1.2.2

WORKDIR /code

COPY pyproject.toml poetry.lock /code/
RUN poetry config installer.max-workers 10
RUN poetry install --no-interaction --no-ansi
CMD mkdir code/csvs
COPY ./src /code/src