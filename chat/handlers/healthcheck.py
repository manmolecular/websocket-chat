from chat.utils.response import Responses


class HealthCheck:
    @staticmethod
    async def get(request):
        """
        Check health status of the application
        :param request: GET request from the user
        :return: JSON with application status
        """
        return Responses.success("Application is up")
