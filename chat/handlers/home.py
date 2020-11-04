from chat.utils.serve import Serve


class Home:
    @staticmethod
    async def get(request):
        """
        Serve the static page for home page.
        :param request: GET request from user
        :return: static page "home.html"
        """
        return Serve.serve_static("home.html")
