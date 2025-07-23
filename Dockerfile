FROM python:3.10.15-slim-bookworm
ENV CRYPTOGRAPHY_DONT_BUILD_RUST 1
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv==0.6.14

WORKDIR /code

COPY requirements.txt /code/
RUN uv pip install -r requirements.txt --system
CMD mkdir code/csvs
COPY ./src /code/src