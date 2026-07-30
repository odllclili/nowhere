FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    NOWHERE_HOME=/data/nowhere \
    PORT=8080

WORKDIR /app

COPY pyproject.toml README.md ./
COPY nowhere ./nowhere
RUN pip install --no-cache-dir .

RUN mkdir -p /data/nowhere

EXPOSE 8080

CMD ["python", "-m", "nowhere.remote"]
