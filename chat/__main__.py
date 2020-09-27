#!/usr/bin/env python3

from aiohttp.web import run_app

from chat.api.app import create_app
from chat.db.base import Base, Engine


def main():
    Base.metadata.create_all(Engine)
    app = create_app()
    run_app(app)


if __name__ == "__main__":
    main()
