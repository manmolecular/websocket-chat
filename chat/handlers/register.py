from chat.db.crud import DatabaseCrud
from chat.utils.response import Responses
from chat.utils.serve import Serve


class Register:
    """
    Handle registration.
    """

    @staticmethod
    async def get(request):
        """
        Serve the static page for registration.
        :param request: GET request from user
        :return: static page "register.html"
        """
        return Serve.serve_static("register.html")

    @staticmethod
    async def post(request):
        """
        Handle REST API requests to "/api/register"

        We get the pair username/password from the POST JSON request body,
        if a user with this pair already exists - we return the error, "User already exists",
        if not - create this user, and return a success message

        :param request: POST request in JSON representation
        :return: JSON response
        """
        credentials = await request.json()
        username = credentials.get("username")
        password = credentials.get("password")

        if DatabaseCrud.check_user_exists(username):
            return Responses.error("User already exists")
        DatabaseCrud.create_user(username, password)
        return Responses.success("User successfully created")
