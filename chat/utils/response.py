from aiohttp.web import json_response


class Responses:
    @staticmethod
    def response(
        status: str, message: str, http_status: int, additional: dict or None = None
    ):
        """
        Define JSON response
        :param status: status explanation
        :param message: message explanation
        :param http_status: HTTP status of response
        :param additional: additional info to response
        :return: web.json_response
        """
        message = {"status": status, "message": message}
        if additional is not None:
            message.update(additional)
        return json_response(message, status=http_status)

    @staticmethod
    def error(
        message: str = "unknown error", status: str = "error", http_status: int = 400
    ):
        """
        Define error JSON response
        :param message: message explanation
        :param status: status explanation
        :param http_status: HTTP status of response
        :return: web.json_response
        """
        return Responses.response(status, message, http_status)

    @staticmethod
    def success(
        message: str = "success", status: str = "success", http_status: int = 200
    ):
        """
        Define success JSON response
        :param message: message explanation
        :param status: status explanation
        :param http_status: HTTP status of response
        :return: web.json_response
        """
        return Responses.response(status, message, http_status)

    @staticmethod
    def success_token(
        token: str,
        username: str,
        status: str = "success",
        message: str = "success",
        http_status: int = 200,
    ):
        """
        Return success message with token
        :param token: JWT token
        :param username: username
        :param status: status explanation
        :param message: message explanation
        :param http_status: HTTP status of response
        :return: web.json_response
        :return:
        """
        return Responses.response(
            status,
            message,
            http_status,
            additional={"token": token, "username": username},
        )
