from asyncio import wait
from collections import deque
from datetime import datetime
from logging import getLogger

from aiohttp import WSMsgType
from aiohttp import web
from aiohttp.web_app import Application

from chat.db.crud import DatabaseCrud
from chat.middlewares.auth import auth_middleware, login_required
from chat.middlewares.auth import cache
from chat.middlewares.auth import get_token, decode_token, get_jti
from chat.utils.config import DefaultPaths

from json import dumps, loads

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
        jti = get_jti()
        jwt_token = get_token(username, jti)
        cache.set(key=username, value=jti)
        response = web.json_response(
            {"status": "success", "message": "Successfully logged in", "token": jwt_token, "username": username}
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
    @staticmethod
    @login_required
    async def get(request):
        return web.FileResponse(path=DefaultPaths.STATIC_TEMPLATES / "chat.html")


class WebSockets:
    def __init__(self):
        self.session_history = deque(maxlen=10)
        self.session_websockets = []

    async def __send_to_all(self, username: str, message: str):
        chat_message = dumps({
            "user": username,
            "message": message,
            "time": f"{datetime.now():%H:%M:%S}"
        })
        self.session_history.append(chat_message)
        DatabaseCrud.save_message(username, message, date_time=datetime.now())

        futures = [client.send_str(chat_message) for client in self.session_websockets]
        if futures:
            await wait(futures)

    async def get(self, request):
        client = web.WebSocketResponse()
        await client.prepare(request)

        for chat_message in self.session_history:
            await client.send_str(chat_message)

        self.session_websockets.append(client)

        username = "unknown"

        try:
            async for message in client:
                if message.type == WSMsgType.TEXT:
                    json_message = loads(message.data.encode("utf-8"))
                    token = json_message.get("token")
                    username = decode_token(token).get("name")
                    message = json_message.get("message")
                    await self.__send_to_all(username, message)
                elif message.type == WSMsgType.ERROR:
                    log.error(
                        f"WebSocket connection closed with exception: {client.exception()}"
                    )
        except:
            self.session_websockets.remove(client)
        finally:
            self.session_websockets.remove(client)

        await self.__send_to_all("server", f"{username} left")


def create_app():
    ws = WebSockets()

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
            web.get("/api/chat/ws", ws.get),
            web.get("/api/health", HealthCheck.get),
            # Static
            web.static("/static/js", path=DefaultPaths.STATIC_JS, append_version=True),
        ]
    )

    return app
