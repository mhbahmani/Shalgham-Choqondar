from json import JSONEncoder

class Response:
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message


class ResponseEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__