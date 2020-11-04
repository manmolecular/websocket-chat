from aiohttp.web import middleware, HTTPForbidden
from aiohttp_csrf import csrf_protect


@middleware
async def csrf(request, handler):
    """
    Add CSRF form protection to "feedback" handler only
    :param request: request from user
    :param handler: trigger handler (who call us?)
    :return: 403 if something wrong with CSRF, else original handler
    """
    if handler.__name__ == "Feedback":
        handler = csrf_protect(handler=handler)
    try:
        return await handler(request)
    except TypeError:
        return HTTPForbidden()
