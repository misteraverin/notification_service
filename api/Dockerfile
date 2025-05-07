FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /home/app
ENV PROMETHEUS_MULTIPROC_DIR=/multiproc_dir

WORKDIR /home/app

# Purge existing libpq and install fresh build dependencies
RUN apt-get update && \
    apt-get purge -y --auto-remove libpq5 libpq-dev && \
    apt-get install -y libpq-dev gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

COPY ./pyproject.toml ./poetry.lock* ./

RUN pip install poetry

# Clear caches and uninstall previous versions before poetry install
RUN poetry cache clear . --all
RUN pip uninstall -y psycopg2 psycopg2-binary || true
RUN poetry install --no-root

RUN mkdir -p $PROMETHEUS_MULTIPROC_DIR

COPY . ./

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]