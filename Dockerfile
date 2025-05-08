FROM public.ecr.aws/docker/library/python:3.13

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  UV_VERSION=0.6.10 \
  UV_LINK_MODE=copy \
  PYTHONPATH=/app

RUN apt update && pip install --upgrade pip

# Install uv
RUN pip install "uv==$UV_VERSION"

WORKDIR /app

COPY uv.lock pyproject.toml /app/

# Install dependencies using uv
RUN uv sync --frozen --no-install-project --no-dev

ADD . /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 80

# Ensure all files in the bin/ folder are executable
RUN chmod +x ./bin/entrypoint.sh

ENTRYPOINT ["./bin/entrypoint.sh"]
