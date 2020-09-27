from pathlib import Path
from random import choices
from string import ascii_uppercase, digits


class DefaultPaths:
    STATIC = Path(__file__).parent.parent.joinpath("static")
    STATIC_TEMPLATES = STATIC.joinpath("templates")
    STATIC_JS = STATIC.joinpath("js")


class JWTConfiguration:
    JWT_SECRET = "".join(choices(ascii_uppercase + digits, k=32))
    JWT_ALGORITHM = "HS256"
    JWT_EXP_DELTA_SECONDS = 60 * 15
