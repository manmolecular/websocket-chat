from asyncio import wait
from collections import deque
from datetime import datetime
from json import dumps, loads

from aiohttp import WSMsgType
from aiohttp import web

from chat.db.crud import DatabaseCrud
from chat.middlewares.auth import decode_token, check_cache
from chat.utils.config import ServiceConfiguration


class WebSockets:
    """
    Manage WebSockets
    """

    def __init__(self, log):
        """
        Save session_history, store 10 messages and show them from history,
        manage current WebSocket connections.
        :param log: logger to use
        """
        self.session_history = deque(maxlen=10)
        self.session_websockets = []
        self.log = log

    async def __send_to_all(self, username: str, message: str) -> None:
        """
        Send message to everybody (basic send function)
        :param username: username of the sender
        :param message: message content of the sender
        :return: None
        """
        chat_message = dumps(
            {"user": username, "message": message, "time": f"{datetime.now():%H:%M:%S}"}
        )
        self.session_history.append(chat_message)
        DatabaseCrud.save_message(username, message, date_time=datetime.now())

        futures = [client.send_str(chat_message) for client in self.session_websockets]
        if futures:
            await wait(futures)

    async def get(self, request):
        """
        Handle WebSocket connection per user
        :param request: WS connection request from browser
        :return: WS connection
        """
        # Check request origin, just in case
        origin = request.headers.get("origin")
        if not any(
            [
                app_origin
                for app_origin in ServiceConfiguration.ORIGIN
                if app_origin in origin
            ]
        ):
            self.log.error("Wrong origin")
            return

        # Origin check passed, check JWT token from first auth-message
        client = web.WebSocketResponse()
        await client.prepare(request)

        try:
            auth = await client.receive_str()
            auth_message = loads(auth)
            auth_token = auth_message.get("token")
            auth_message = auth_message.get("message")
            assert auth_message == "auth"
            payload = decode_token(auth_token)
            if check_cache(payload) is False:
                raise ValueError("Token is not active")
            username = payload.get("name", "unknown")

        except:
            message = "Not authorized"
            await client.send_str(message)
            self.log.error(message)
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
                    self.log.error(
                        f"WebSocket connection closed with exception: {client.exception()}"
                    )
        finally:
            self.session_websockets.remove(client)

        await self.__send_to_all("server", f"User {username} left the server")
