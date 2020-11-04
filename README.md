# websocket-chat
Simple WebSocket chat based on the aiohttp library

## Stack
- Auth: JWT + JTI (JWT id)
- Cache: Redis
- Database: PostgreSQL
- ORM: SQLAlchemy
- Backend: Aiohttp
- Frontend: Pure JS + Bootstrap
- Language: Python 3.8
- Deploy: Docker + docker-compose
- Additional: CSRF with aiohttp

## Prepare
Optional: create `.env` file with the following variables if you want to overwrite default `docker-compose.yml` environment variables:
```
POSTGRES_DATABASE=...
POSTGRES_PASSWORD=...
POSTGRES_USER=...
POSTGRES_HOST=...
POSTGRES_PORT=...
REDIS_HOST=...
JWT_SECRET=...
ORIGIN=...
```
## Run
```
docker-compose up -d
```
```
http://localhost:8080/
```