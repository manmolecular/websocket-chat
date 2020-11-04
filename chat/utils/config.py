from os import environ
from pathlib import Path

from chat.utils.helpers import generate_random


class DefaultPaths:
    """
    Define the default paths for application.
    Static - for static files (js, templates, styles, etc.)
    Additionally,
    Static templates - subdirectory with templates
    Static js - subdirectory with js
    """

    STATIC = Path(__file__).parent.parent.joinpath("static")
    STATIC_TEMPLATES = STATIC.joinpath("templates")
    STATIC_JS = STATIC.joinpath("js")


class DbValues:
    """
    Define database values.
    Retrieve them from environment (docker, for example).
    """

    POSTGRES_HOST = environ.get("POSTGRES_HOST", default="localhost")
    POSTGRES_PORT = environ.get("POSTGRES_PORT", default="5432")

    # Use env only
    POSTGRES_DATABASE = environ.get("POSTGRES_DATABASE")
    POSTGRES_PASSWORD = environ.get("POSTGRES_PASSWORD")
    POSTGRES_USER = environ.get("POSTGRES_USER")


class JWTConfiguration:
    """
    Define JWT configuration, take JWT secret from the env
    variable or generate the fallback.
    Expiration = seconds * minutes, use it as you wish (15 minutes for now)
    """

    JWT_SECRET = environ.get("JWT_SECRET") or generate_random(length=32)
    JWT_ALGORITHM = "HS256"
    JWT_EXP_DELTA_SECONDS = 60 * 15


class CacheValues:
    """
    Define cache values. Set redis key expiration time the same
    as the JWT expiration time.
    """

    REDIS_EXP = JWTConfiguration.JWT_EXP_DELTA_SECONDS
    REDIS_HOST = environ.get("REDIS_HOST", default="localhost")


class CSRFCongiruation:
    """
    Define CSRF token fields, form fields and cookie name
    """

    FORM_FIELD_NAME = "_csrf_token"
    COOKIE_NAME = "csrf_token"


class ServiceConfiguration:
    """
    Define service options
    """

    ORIGIN = (
        [environ.get("ORIGIN")] if environ.get("ORIGIN") else ["0.0.0.0", "localhost"]
    )
