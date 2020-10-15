from datetime import datetime, timedelta
from random import choice
from string import ascii_lowercase, ascii_uppercase

import jwt
from aiohttp import web

from chat.cache.storage import RedisCache
from chat.utils.config import JWTConfiguration

cache = RedisCache()


def decode_token(jwt_token):
    return jwt.decode(
        jwt_token,
        JWTConfiguration.JWT_SECRET,
        algorithms=[JWTConfiguration.JWT_ALGORITHM],
    )


async def auth_middleware(app, handler):
    async def middleware(request):
        request.user = None
        jwt_token = request.headers.get("Authorization")
        if jwt_token:
            jwt_token = jwt_token.split(" ")[1]
        if jwt_token:
            try:
                payload = decode_token(jwt_token)
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return web.Response(text="Token is invalid, decode error", status=400)
            try:
                username = payload.get("name")
                jti = payload.get("jti")
                jti_cache = cache.get(username).decode(encoding="utf-8")
                if jti != jti_cache:
                    return web.Response(text="Token is invalid, cache expired or not exists", status=400)
            except:
                return web.Response(text="Token is invalid, not found in cache", status=400)
            request.user = username
        return await handler(request)

    return middleware


def get_jti(length: int = 32):
    return "".join(choice(ascii_lowercase + ascii_uppercase) for _ in range(length))


def get_token(username: str, jti: str):
    time_iat = datetime.utcnow()
    time_exp = timedelta(seconds=JWTConfiguration.JWT_EXP_DELTA_SECONDS)
    payload = {
        "name": username,
        "jti": jti,
        "iat": time_iat,
        "exp": time_iat + time_exp,
    }
    jwt_token = jwt.encode(
        payload, JWTConfiguration.JWT_SECRET, JWTConfiguration.JWT_ALGORITHM
    )
    return jwt_token.decode("utf-8")


def login_required(func):
    def wrapper(request, *args, **kwargs):
        if not request.user:
            return web.Response(text="Auth required", status=401)
        return func(request)

    return wrapper
