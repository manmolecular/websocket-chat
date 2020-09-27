import jwt
from aiohttp import web

from chat.utils.config import JWTConfiguration


async def auth_middleware(app, handler):
    async def middleware(request):
        request.user = None
        jwt_token = request.cookies.get("access_token")
        if jwt_token:
            try:
                payload = jwt.decode(
                    jwt_token,
                    JWTConfiguration.JWT_SECRET,
                    algorithms=[JWTConfiguration.JWT_ALGORITHM],
                )
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return web.Response(text="Token is invalid", status=400)
            request.user = payload.get("user_id")
        return await handler(request)

    return middleware


def login_required(func):
    def wrapper(request):
        if not request.user:
            return web.Response(text="Auth required", status=401)
        return func(request)

    return wrapper
