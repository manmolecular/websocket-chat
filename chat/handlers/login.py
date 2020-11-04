from chat.db.crud import DatabaseCrud
from chat.middlewares.auth import cache
from chat.middlewares.auth import get_token, get_jti
from chat.utils.response import Responses
from chat.utils.serve import Serve
from chat.middlewares.auth import decode_token, check_cache


class Login:
    """
    Handle authentication.
    """

    @staticmethod
    async def get(request):
        """
        Serve the static page for login.
        :param request: GET request from user
        :return: static page "login.html"
        """
        return Serve.serve_static("login.html")

    @staticmethod
    async def post(request):
        """
        Handle REST API requests to "/api/login"

        We get the pair username/password from the POST JSON request body,
        if this pair username/password is incorrect - we return the error message "Wrong username or password",
        if everything is correct, we generate the JTI identifier, take the JWT token with the JTI value,
        save the cache pair username/JTI in the Redis cache database to have revocation possibility,
        and finally, we return the JSON response, containing status + message + token itself and username

        :param request: POST request in JSON representation
        :return: JSON response
        """
        credentials = await request.json()
        username = credentials.get("username")
        password = credentials.get("password")

        # Check if already logged in
        try:
            jwt_token = request.headers.get("Authorization")
            jwt_token = jwt_token.split(" ")[1]
            payload = decode_token(jwt_token)
            if check_cache(payload) is True:
                return Responses.error("Already logged in, log out")
        except Exception:
            pass

        if not DatabaseCrud.check_credentials(username, password):
            return Responses.error("Wrong username or password")
        jti = get_jti()
        jwt_token = get_token(username, jti)
        cache.set(key=username, value=jti)
        return Responses.success_token(jwt_token, username, message="Successfully logged in")
