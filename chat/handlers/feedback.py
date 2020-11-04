from aiohttp import web
from aiohttp_csrf import generate_token

from chat.utils.config import DefaultPaths, CSRFCongiruation


class Feedback(web.View):
    async def get(self):
        """
        Serve the static page for feedback, manage CSRF tokens
        :return: static page "feedback.html"
        """
        token = await generate_token(self.request)
        with open(
            file=DefaultPaths.STATIC_TEMPLATES / "feedback.html", mode="r"
        ) as template:
            body = template.read()
        body = body.format(field_name=CSRFCongiruation.FORM_FIELD_NAME, token=token)
        return web.Response(text=body, content_type="text/html")

    async def post(self):
        """
        Handle POST request with feedback information
        :return: HTML with basic info message
        """
        post = await self.request.post()
        body = 'Thanks! We will send the e-mail to {email}<br><span>go to the <a href="/">home page</a></span>'.format(
            email=post["email"]
        )
        return web.Response(text=body, content_type="text/html")
