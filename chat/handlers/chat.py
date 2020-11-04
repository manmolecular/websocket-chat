from chat.middlewares.auth import login_required
from chat.utils.serve import Serve


class Chat:
    @staticmethod
    @login_required
    async def get(request):
        """
        Serve chat page
        :param request: GET request from user
        :return: static page "chat.html"
        """
        return Serve.serve_static("chat.html")
