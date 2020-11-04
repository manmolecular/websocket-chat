from chat.utils.config import DefaultPaths
from aiohttp.web import FileResponse


class Serve:
    @staticmethod
    def serve_static(template: str, path=DefaultPaths.STATIC_TEMPLATES):
        """
        Serve static files easily
        :param template: template file name
        :param path: path to directory
        :return: file response
        """
        return FileResponse(path=path / template)
