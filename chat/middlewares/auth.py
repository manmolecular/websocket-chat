import jwt
from aiohttp import web

from chat.utils.config import JWTConfiguration

from datetime import datetime, timedelta


async def auth_middleware(app, handler):
    async def middleware(request):
        request.user = None
        jwt_token = request.headers.get("Authorization")
        if jwt_token:
            jwt_token = jwt_token.split(" ")[1]
        if jwt_token:
            try:
                payload = jwt.decode(
                    jwt_token,
                    JWTConfiguration.JWT_SECRET,
                    algorithms=[JWTConfiguration.JWT_ALGORITHM],
                )
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return web.Response(text="Token is invalid", status=400)
            request.user = payload.get("name")
        return await handler(request)

    return middleware


def get_token(username: str):
    time_iat = datetime.utcnow()
    time_exp = timedelta(seconds=JWTConfiguration.JWT_EXP_DELTA_SECONDS)
    payload = {
        "name": username,
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
