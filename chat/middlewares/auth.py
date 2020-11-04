from datetime import datetime, timedelta

import jwt
from aiohttp import web

from chat.cache.storage import RedisCache
from chat.utils.config import JWTConfiguration
from chat.utils.helpers import generate_random

# Init redis connection
cache = RedisCache()


def decode_token(jwt_token):
    """
    Decode and verify (iat, exp, sign, etc.) JWT token
    :param jwt_token: JWT token to decode in str representation
    :return: decoded JWT token
    """
    return jwt.decode(
        jwt=jwt_token,
        key=JWTConfiguration.JWT_SECRET,
        algorithms=[JWTConfiguration.JWT_ALGORITHM],
        verify=True,
        options={
            "verify_iat": True,
            "verify_exp": True
        }
    )


def check_cache(payload):
    """
    Check that this username with this JTI exists in cache, and active
    :param payload: payload to user as a base
    :return: True if exists, else False
    """
    username = payload.get("name")
    jti = payload.get("jti")
    jti_cache = cache.get(username).decode(encoding="utf-8")
    if jti != jti_cache:
        return False
    return True


async def auth_middleware(app, handler):
    """
    Create own middleware to check users authorization JWT tokens, and so on.
    :param app: web-application entity
    :param handler: trigger handler (who call us here?)
    :return: original handler with checked user (we check here, that user data is ok)
    """
    async def middleware(request):
        request.user = None
        jwt_token = request.headers.get("Authorization")
        if jwt_token:
            jwt_token = jwt_token.split(" ")[1]
        if jwt_token:
            try:
                payload = decode_token(jwt_token)
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                return web.HTTPForbidden()
            try:
                if check_cache(payload) is False:
                    return web.HTTPUnauthorized()
            except:
                return web.HTTPUnauthorized()
            request.user = payload.get("name")
        return await handler(request)

    return middleware


def get_jti(length: int = 32):
    """
    Generate JTI value
    :param length: length, 32 by default
    :return: random str value (JTI)
    """
    return generate_random(length)


def get_token(username: str, jti: str):
    """
    Create JWT token, including username + JTI
    :param username: username
    :param jti: JTI value (from get_jti(), for example)
    :return: JWT token
    """
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
    """
    This deco will return HTTP 403 if user is not logged in (checked with auth_middleware)
    :param func: handler call
    :return: function wrapper
    """
    def wrapper(request, *args, **kwargs):
        if not request.user:
            return web.HTTPUnauthorized()
        return func(request)

    return wrapper
