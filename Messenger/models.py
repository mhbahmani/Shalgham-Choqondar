from json import JSONEncoder


class User:
    def __init__(self, username, password) -> None:
        self.username: str = username
        self.password: str = password
        self.chatrooms: dict = {}

    def get_chatrooms(self) -> dict:
        chatrooms = {}
        for chatroom in self.chatrooms:
            chatroom: ChatRoom
            chatrooms[chatroom] = self.chatrooms[chatroom].num_unreed_messages
        return chatrooms

    def add_new_chatroom(self, other_user):
        self.chatrooms[other_user.username] = ChatRoom(self, other_user)
        other_user.chatrooms[self.username] = ChatRoom(other_user, self)

    def _is_valid_username(username, users):
        for user in users:
            if user.username == username:
                raise ValueError("Duplicate Username")
        return username


class ChatRoom:
    def __init__(self, user: User, contact: User) -> None:
        self.user: User = user
        self.contact: User = contact
        self.messages: list = []
        self.unreaded_messages: list = []
        self.num_unreed_messages = 0

    def get_messages(self):
        self.num_unreed_messages = 0
        self.unreaded_messages.clear()
        return "\n".join([f"{'' if msg.sender == self.user else f'{msg.sender.username}) '}{msg.text}" for msg in self.messages])

    def add_message(self, text: str) -> None:
        message = Message(self.user, text)
        self.messages.append(message)
        self.contact.chatrooms[self.user.username].messages.append(message)
        self.contact.chatrooms[self.user.username].unreaded_messages.append(message)

    def get_unread_messages(self):
        msgs = self.unreaded_messages.copy()
        self.unreaded_messages.clear()
        return "\n".join([f"{'' if msg.sender == self.user else f'{msg.sender.username}) '}{msg.text}" for msg in msgs])

class Message:
    def __init__(self, user: User, text: str) -> None:
        self.sender: User = user
        self.text: str = text


class Response:
    def __init__(self, status_code: int, message: str, data: dict = {}) -> None:
        self.status_code = status_code
        self.data = data
        self.message = message


class ResponseEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
