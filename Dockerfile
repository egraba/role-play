FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies.
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /code

WORKDIR /code

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen --no-install-project --no-dev
COPY . /code

EXPOSE 8000

CMD ["invoke", "prod.run"]
