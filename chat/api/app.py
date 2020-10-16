import logging
from asyncio import wait
from collections import deque
from datetime import datetime
from json import dumps, loads

import aiohttp_csrf
from aiohttp import WSMsgType
from aiohttp import web
from aiohttp.web_app import Application

from chat.db.crud import DatabaseCrud
from chat.middlewares.auth import auth_middleware, login_required
from chat.middlewares.auth import cache
from chat.middlewares.auth import get_token, decode_token, get_jti
from chat.utils.config import DefaultPaths

FORM_FIELD_NAME = '_csrf_token'
COOKIE_NAME = 'csrf_token'


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


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
            {
                "status": "success",
                "message": "Successfully logged in",
                "token": jwt_token,
                "username": username,
            }
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


class Feedback(web.View):
    async def get(self):
        token = await aiohttp_csrf.generate_token(self.request)
        with open(file=DefaultPaths.STATIC_TEMPLATES / "feedback.html", mode="r") as template:
            body = template.read()
        body = body.format(field_name=FORM_FIELD_NAME, token=token)
        return web.Response(body=body.encode("utf-8"), content_type="text/html")

    async def post(self):
        post = await self.request.post()
        body = "Thanks! We will send the e-mail to {email}".format(email=post['email'])
        return web.Response(body=body.encode('utf-8'), content_type='text/html',)


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
        chat_message = dumps(
            {"user": username, "message": message, "time": f"{datetime.now():%H:%M:%S}"}
        )
        self.session_history.append(chat_message)
        DatabaseCrud.save_message(username, message, date_time=datetime.now())

        futures = [client.send_str(chat_message) for client in self.session_websockets]
        if futures:
            await wait(futures)

    async def get(self, request):
        origin = request.headers.get("origin")
        # FIXME: Dumb validation, fix the scope
        if not any([app_origin for app_origin in ("0.0.0.0", "localhost") if app_origin in origin]):
            log.error("Wrong origin")
            return

        client = web.WebSocketResponse()
        await client.prepare(request)

        try:
            auth = await client.receive_str()
            auth_message = loads(auth)
            auth_token = auth_message.get("token")
            auth_message = auth_message.get("message")
            assert auth_message == "auth"
            username = decode_token(auth_token).get("name", "unknown")
        except:
            message = "Not authorized"
            await client.send_str(message)
            log.error(message)
            return

        await self.__send_to_all("server", f"User {username} joined the server")

        for chat_message in self.session_history:
            await client.send_str(chat_message)

        self.session_websockets.append(client)

        try:
            async for message in client:
                if message.type == WSMsgType.TEXT:
                    message_data = message.data.encode("utf-8")
                    message_json = loads(message_data)
                    message_text = message_json.get("message")
                    await self.__send_to_all(username, message_text)
                elif message.type == WSMsgType.ERROR:
                    log.error(
                        f"WebSocket connection closed with exception: {client.exception()}"
                    )
        finally:
            self.session_websockets.remove(client)

        await self.__send_to_all("server", f"User {username} left the server")


@web.middleware
async def csrf(request, handler):
    if handler.__name__ == "Feedback":
        handler = aiohttp_csrf.csrf_protect(handler=handler)
    try:
        return await handler(request)
    except TypeError:
        return web.HTTPForbidden()


def create_app():
    ws = WebSockets()

    csrf_policy = aiohttp_csrf.policy.FormPolicy(FORM_FIELD_NAME)
    csrf_storage = aiohttp_csrf.storage.CookieStorage(COOKIE_NAME)

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
            # Feedback
            web.view("/feedback", Feedback)
        ]
    )

    aiohttp_csrf.setup(app, policy=csrf_policy, storage=csrf_storage)
    app.middlewares.append(csrf)
    return app
