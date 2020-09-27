FROM python:3.8-alpine as websocket-chat

LABEL org.label-schema.name="WebSocket Chat" \
      org.label-schema.description="WebSocket Chat" \
      org.label-schema.license="GPL-2.0"

COPY . /app/
COPY docker/wait-for-it.sh /app/wait-for-it.sh
WORKDIR /app
RUN apk add --no-cache --virtual .build_deps build-base gcc musl-dev libffi-dev openssl-dev && \
    apk add --no-cache postgresql-dev bash curl && \
    pip install --no-cache-dir -r requirements.txt && \
    chmod +x wait-for-it.sh

EXPOSE 8080
ENTRYPOINT ["./wait-for-it.sh", "-t", "5", "chat-db:5432", "--", "python3", "-m", "chat"]