FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /usr/local/terminusgps-site
ENV DJANGO_SETTINGS_MODULE="src.settings.dev"
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE="copy"
ENV UV_NO_SYNC=1

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy and install project
COPY . /usr/local/terminusgps-site
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Activate virtual environment
ENV PATH="/usr/local/terminusgps-site/.venv/bin:$PATH"

ENTRYPOINT []

RUN uv run manage.py migrate

CMD ["uv", "run", "manage.py", "runserver", "0.0.0.0:8000", "--noreload"]

EXPOSE 8000
