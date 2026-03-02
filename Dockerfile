FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN pip install uv

RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

RUN chown -R app:app /app
USER app

EXPOSE 8000

CMD ["bash", "start.sh"]
