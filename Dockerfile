FROM python:latest

RUN pip install poetry

WORKDIR /src

COPY . /src

RUN poetry install --no-root

CMD ["poetry", "run", "python", "src/main.py"]
