class User:
    def __init__(self, username, password) -> None:
        self.username: str = username
        self.password: str = password
        self.chat_rooms: list = []


class ChatRoom:
    def __init__(self, contact) -> None:
        self.contact: User = contact
        self.messages: list = []


class Message:
    def __init__(self, user: User, text: str) -> None:
        self.sender: User = user
        self.text: str = text