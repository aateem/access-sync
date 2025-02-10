# Stage 1: Build the application
FROM python:3.12-alpine as builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install -U pip && pip install -U build

COPY . .

RUN python -m build --wheel

FROM python:3.12-alpine

WORKDIR /app

COPY --from=builder /app/dist/*.whl /app/

RUN pip install --no-cache-dir /app/*.whl

ENTRYPOINT ["am"]

CMD ["--help"]