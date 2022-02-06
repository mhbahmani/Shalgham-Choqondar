from json import JSONEncoder


class Response:
    def __init__(self, status_code: int, message: str, date: list) -> None:
        self.status_code = status_code
        self.data = []
        self.message = message


class ResponseEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
