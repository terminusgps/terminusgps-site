FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /usr/local/terminusgps-site
ENV DJANGO_SETTINGS_MODULE="src.settings.prod"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_SYNC=1
ENV HTTPS=on

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /usr/local/terminusgps-site

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

ENV PATH="/usr/local/terminusgps-site/.venv/bin:$PATH"

ENTRYPOINT []

CMD ["uv", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "src.wsgi"]

EXPOSE 8000
