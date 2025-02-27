FROM python:3.12-slim-bullseye

ENV UID=1001 \
    GID=1001 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    DOCKERIZE_VERSION=v0.9.2 \
    PATH="$PATH:/root/.local/bin"

RUN apt-get update \
  && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    gettext \
    git \
    libpq-dev \
    wget \
    libffi-dev \
  && apt-get autoremove -y && apt-get clean -y && rm -rf /var/lib/apt/lists/* \
  && wget "https://github.com/jwilder/dockerize/releases/download/${DOCKERIZE_VERSION}/dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && tar -C /usr/local/bin -xzvf "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" \
  && rm "dockerize-linux-amd64-${DOCKERIZE_VERSION}.tar.gz" && dockerize --version \
  && pip install -U pip \
  && curl -LsSf https://astral.sh/uv/install.sh | sh \
  && uv --version

WORKDIR /code

COPY ./uv.lock ./pyproject.toml /code/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/code/.venv/bin:$PATH"

RUN groupadd -r tg_bot && useradd -d /code -r -g tg_bot tg_bot && chown tg_bot:tg_bot -R /code

RUN usermod -u $UID tg_bot && groupmod -g $GID tg_bot


USER tg_bot:tg_bot

COPY --chown=tg_bot:tg_bot alembic /code/alembic
COPY --chown=tg_bot:tg_bot src /code/src
COPY --chown=tg_bot:tg_bot scripts/* /code/
COPY --chown=tg_bot:tg_bot alembic.ini /code/
COPY --chown=tg_bot:tg_bot main.py /code/
COPY --chown=tg_bot:tg_bot .env /code/

RUN chmod +x /code/entrypoint.sh
