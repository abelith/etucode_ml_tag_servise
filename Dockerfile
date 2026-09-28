FROM python:3.14.7-slim
# install uv
COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# install system compilers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev && \
    uv run python  \
    -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('cointegrated/rubert-tiny2')"

COPY . .

EXPOSE 8080

ENTRYPOINT ["uv", "run", "python3", "main.py"]