from json import JSONEncoder


class Response:
    def __init__(self, status_code: int, message: str, data: list = []) -> None:
        self.status_code = status_code
        self.data = data
        self.message = message


class ResponseEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__


class ResponseDecoder:
    def decode(dct):
        if len(dct) == 3 and dct.get("status_code"):
            return Response(dct['status_code'], dct['message'], dct['data'])
        return dct