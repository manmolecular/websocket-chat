from pathlib import Path


class DefaultPaths:
    STATIC = Path("static")
    STATIC_TEMPLATES = STATIC.joinpath("templates")
    STATIC_JS = STATIC.joinpath("js")


class JWTConfiguration:
    JWT_SECRET = "secret"
    JWT_ALGORITHM = "HS256"
    JWT_EXP_DELTA_SECONDS = 60 * 15
