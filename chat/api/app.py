import logging

import aiohttp_csrf
from aiohttp import web
from aiohttp.web_app import Application

from chat.handlers.chat import Chat
from chat.handlers.feedback import Feedback
from chat.handlers.healthcheck import HealthCheck
from chat.handlers.home import Home
from chat.handlers.login import Login
from chat.handlers.logout import Logout
from chat.handlers.register import Register
from chat.handlers.websockets import WebSockets
from chat.middlewares.auth import auth_middleware
from chat.middlewares.csrf import csrf
from chat.utils.config import DefaultPaths, CSRFCongiruation

# Define logging to console
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


def create_app():
    """
    Create basic application, define API endpoints
    :return: web app
    """
    ws = WebSockets(log)

    csrf_policy = aiohttp_csrf.policy.FormPolicy(CSRFCongiruation.FORM_FIELD_NAME)
    csrf_storage = aiohttp_csrf.storage.CookieStorage(CSRFCongiruation.COOKIE_NAME)

    app = Application(middlewares=[auth_middleware])
    app.add_routes(
        routes=[
            # Render
            web.get("/register", Register.get),
            web.get("/login", Login.get),
            web.get("/chat", Chat.get),
            web.get("/", Home.get),
            # Api
            web.post("/api/register", Register.post),
            web.post("/api/login", Login.post),
            web.post("/api/logout", Logout.post),
            web.get("/api/chat/ws", ws.get),
            web.get("/api/health", HealthCheck.get),
            # Static
            web.static("/static/js", path=DefaultPaths.STATIC_JS, append_version=True),
            # Feedback
            web.view("/feedback", Feedback),
        ]
    )

    aiohttp_csrf.setup(app, policy=csrf_policy, storage=csrf_storage)
    app.middlewares.append(csrf)
    return app
