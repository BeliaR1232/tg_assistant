FROM python:3.12-slim-bullseye

ENV POETRY_VERSION=1.8.5 \
    UID=1001 \
    GID=1001 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    DOCKERIZE_VERSION=v0.9.2 \
    POETRY_VERSION=1.8.5 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
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
  && curl -sSL 'https://install.python-poetry.org' | python \
  && poetry --version

WORKDIR /code

COPY ./poetry.lock ./pyproject.toml /code/

RUN poetry install

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
