from asyncio import wait
from collections import deque
from datetime import datetime, timedelta
from logging import getLogger

import jwt
from aiohttp import WSMsgType
from aiohttp import web
from aiohttp.web_app import Application

from chat.db.crud import DatabaseCrud
from chat.middlewares.auth import auth_middleware, login_required
from chat.utils.config import DefaultPaths
from chat.utils.config import JWTConfiguration

log = getLogger(__name__)


class Register(web.View):
    async def get(self):
        return web.FileResponse(path=DefaultPaths.STATIC_TEMPLATES / "register.html")

    async def post(self):
        credentials = await self.request.post()
        username = credentials.get("username")
        password = credentials.get("password")
        DatabaseCrud.create_user(username, password)
        return web.json_response(
            {"status": "success", "message": "successfully registered"}
        )


class Login(web.View):
    async def get(self):
        return web.FileResponse(path=DefaultPaths.STATIC_TEMPLATES / "login.html")

    async def post(self):
        credentials = await self.request.post()
        username = credentials.get("username")
        password = credentials.get("password")
        if not DatabaseCrud.check_credentials(username, password):
            return web.Response(text="Wrong username or password", status=400)
        payload = {
            "user_id": username,
            "exp": datetime.utcnow()
            + timedelta(seconds=JWTConfiguration.JWT_EXP_DELTA_SECONDS),
        }
        jwt_token = jwt.encode(
            payload, JWTConfiguration.JWT_SECRET, JWTConfiguration.JWT_ALGORITHM
        )
        response = web.json_response(
            {"status": "success", "message": "successfully logged in",}
        )
        response.set_cookie(
            name="access_token", value=jwt_token.decode("utf-8"), httponly="True"
        )
        return response


class Chat:
    def __init__(self):
        self.session_history = deque(maxlen=10)
        self.session_websockets = []

    @staticmethod
    @login_required
    async def chat(request):
        return web.FileResponse(path=DefaultPaths.STATIC_TEMPLATES / "chat.html")

    @staticmethod
    async def home(request):
        return web.HTTPFound("/chat")

    async def send_to_all(self, username: str, message: str):
        chat_message = f"{datetime.now():%H:%M:%S} – {username}: {message}"
        self.session_history.append(chat_message)
        DatabaseCrud.save_message(username, message, date_time=datetime.now())

        futures = [client.send_str(chat_message) for client in self.session_websockets]
        if futures:
            await wait(futures)

    async def websockets(self, request):
        client = web.WebSocketResponse()
        await client.prepare(request)

        username = request.user

        await self.send_to_all("server", f"{username} joined!")

        for chat_message in self.session_history:
            await client.send_str(chat_message)

        self.session_websockets.append(client)

        try:
            async for message in client:
                if message.type == WSMsgType.TEXT:
                    await self.send_to_all(username, message.data)
                elif message.type == WSMsgType.ERROR:
                    log.error(
                        f"WebSocket connection closed with exception: {client.exception()}"
                    )
        finally:
            self.session_websockets.remove(client)

        await self.send_to_all("server", f"{username} left")


def create_app():
    chat = Chat()

    app = Application(middlewares=[auth_middleware])
    app.add_routes(
        routes=[
            web.view("/register", Register),
            web.view("/login", Login),
            web.get("/", chat.home),
            web.get("/chat", chat.chat),
            web.get("/chat/ws", chat.websockets),
            web.static("/static/js", path=DefaultPaths.STATIC_JS, append_version=True),
        ]
    )

    return app
