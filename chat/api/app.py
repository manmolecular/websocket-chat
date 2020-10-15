from asyncio import wait
from collections import deque
from datetime import datetime, timedelta
from logging import getLogger

from aiohttp import WSMsgType
from aiohttp import web
from aiohttp.web_app import Application

from chat.db.crud import DatabaseCrud
from chat.middlewares.auth import auth_middleware, login_required
from chat.utils.config import DefaultPaths
from chat.middlewares.auth import get_token

log = getLogger(__name__)


class Register:
    @staticmethod
    async def get(request):
        return web.FileResponse(path=DefaultPaths.STATIC_TEMPLATES / "register.html")

    @staticmethod
    async def post(request):
        credentials = await request.json()
        username = credentials.get("username")
        password = credentials.get("password")
        if DatabaseCrud.check_user_exists(username):
            return web.json_response(
                {"status": "error", "message": "User already exists"}, status=400
            )
        DatabaseCrud.create_user(username, password)
        return web.json_response(
            {"status": "success", "message": "User successfully created"}
        )


class Login:
    @staticmethod
    async def get(request):
        return web.FileResponse(path=DefaultPaths.STATIC_TEMPLATES / "login.html")

    @staticmethod
    async def post(request):
        credentials = await request.json()
        username = credentials.get("username")
        password = credentials.get("password")
        if not DatabaseCrud.check_credentials(username, password):
            return web.json_response(
                {"status": "error", "message": "Wrong username or password"}, status=400
            )
        jwt_token = get_token(username)
        response = web.json_response(
            {"status": "success", "message": "Successfully logged in", "token": jwt_token}
        )
        return response


class Home:
    @staticmethod
    async def get(request):
        return web.FileResponse(path=DefaultPaths.STATIC_TEMPLATES / "home.html")


class HealthCheck:
    @staticmethod
    async def get(request):
        return web.json_response({"status": "success", "message": "Application is up"})


class Chat:
    def __init__(self):
        self.session_history = deque(maxlen=10)
        self.session_websockets = []

    @staticmethod
    @login_required
    async def get(request):
        return web.FileResponse(path=DefaultPaths.STATIC_TEMPLATES / "chat.html")

    async def __send_to_all(self, username: str, message: str):
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

        await self.__send_to_all("server", f"{username} joined!")

        for chat_message in self.session_history:
            await client.send_str(chat_message)

        self.session_websockets.append(client)

        try:
            async for message in client:
                if message.type == WSMsgType.TEXT:
                    await self.__send_to_all(username, message.data)
                elif message.type == WSMsgType.ERROR:
                    log.error(
                        f"WebSocket connection closed with exception: {client.exception()}"
                    )
        finally:
            self.session_websockets.remove(client)

        await self.__send_to_all("server", f"{username} left")


def create_app():
    chat_handler = Chat()

    app = Application(middlewares=[auth_middleware])
    app.add_routes(
        routes=[
            # Render
            web.get("/register", Register.get),
            web.get("/login", Login.get),
            web.get("/chat", chat_handler.get),
            web.get("/", Home.get),
            # Api
            web.post("/api/register", Register.post),
            web.post("/api/login", Login.post),
            web.get("/api/chat/ws", chat_handler.websockets),
            web.get("/api/health", HealthCheck.get),
            # Static
            web.static("/static/js", path=DefaultPaths.STATIC_JS, append_version=True),
        ]
    )

    return app
