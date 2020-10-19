from os import environ
from pathlib import Path

from chat.utils.helpers import generate_random


class DefaultPaths:
    STATIC = Path(__file__).parent.parent.joinpath("static")
    STATIC_TEMPLATES = STATIC.joinpath("templates")
    STATIC_JS = STATIC.joinpath("js")


class DbValues:
    POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE", default="chat")
    POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD", default="pass")
    POSTGRES_USER = environ.get("POSTGRES_USER", default="user")
    POSTGRES_HOST = environ.get("POSTGRES_HOST", default="localhost")
    POSTGRES_PORT = environ.get("POSTGRES_PORT", default="5432")


class JWTConfiguration:
    JWT_SECRET = generate_random(length=32)
    JWT_ALGORITHM = "HS256"
    JWT_EXP_DELTA_SECONDS = 60 * 15


class CacheValues:
    REDIS_EXP = JWTConfiguration.JWT_EXP_DELTA_SECONDS
    # REDIS_EXP = 10
    REDIS_HOST = environ.get("REDIS_HOST", default="localhost")
