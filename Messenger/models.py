from json import JSONEncoder


class User:
    def __init__(self, username, password) -> None:
        self.username: str = username
        self.password: str = password
        self.chat_rooms: list = []

    def _is_valid_username(username, users):
        for user in users:
            if user.username == username:
                raise ValueError("Duplicate Username")
        return username


class ChatRoom:
    def __init__(self, contact) -> None:
        self.contact: User = contact
        self.messages: list = []


class Message:
    def __init__(self, user: User, text: str) -> None:
        self.sender: User = user
        self.text: str = text


class Response:
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message


class ResponseEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
