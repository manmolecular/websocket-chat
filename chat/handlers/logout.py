from aiohttp.web import HTTPUnauthorized

from chat.middlewares.auth import cache
from chat.middlewares.auth import decode_token, check_cache
from chat.middlewares.auth import login_required
from chat.utils.response import Responses


class Logout:
    """
    Handle logout function
    """

    @staticmethod
    @login_required
    async def post(request):
        """
        Handle REST API requests to "/api/logout"

        First of all, we check that request contains an "Authorization" header with
        some value, if not - we can't logout user that is not logged in, return an error JSON response.
        Else, if the JWT token exists, we need to decode it to remove the key from the Redis cache
        database. If everything is ok, the user successfully logged out.

        :param request: POST request in JSON representation
        :return: JSON response
        """
        jwt_token = request.headers.get("Authorization")
        if not jwt_token:
            return HTTPUnauthorized()
        try:
            jwt_token = jwt_token.split(" ")[1]
            payload = decode_token(jwt_token)
            if check_cache(payload) is False:
                raise ValueError("Token is not active")
            username = payload.get("name")
            cache.delitem(username)
        except ValueError as not_active:
            return Responses.error(str(not_active))
        except Exception:
            return Responses.error("Token revocation error")
        finally:
            return Responses.success("Successfully logged out")
