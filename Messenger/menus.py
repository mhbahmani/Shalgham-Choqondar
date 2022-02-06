from meta import SingletonMeta

import re


class CommandHandler(metaclass=SingletonMeta):
    SIGNUP = "Signup"
    LOGIN = "Login"

    OPEN_CHATROOM = "OpenChatroom"
    SEND_MESSAGE = "SendMessage"
    UPDATE_CHATROOM = "UpdateChatroom"


    def __init__(self) -> None:
        from messenger import MessengerServer
        self.commands = [
            Command(
                CommandHandler.SIGNUP,
                re.compile(f"(?P<session_id>[\w|=]+)::{CommandHandler.SIGNUP}::(?P<username>\w+)\|,\|(?P<password>\w+)"), 
                MessengerServer.signup, self),
            Command(
                CommandHandler.LOGIN,
                re.compile(f"(?P<session_id>[\w|=]+)::{CommandHandler.LOGIN}::(?P<username>\w+)\|,\|(?P<password>\w+)"),
                MessengerServer.login, self),
            Command(
                CommandHandler.OPEN_CHATROOM,
                re.compile(f"(?P<session_id>[\w|=]+)::{CommandHandler.OPEN_CHATROOM}::(?P<username>\w+)"),
                MessengerServer.open_chatroom, self),
            Command(
                CommandHandler.SEND_MESSAGE,
                re.compile(f"(?P<session_id>[\w|=]+)::{CommandHandler.SEND_MESSAGE}::(?P<contact>\w+)\|,\|(?P<message>.+)"),
                MessengerServer.send_message, self),
            Command(
                CommandHandler.UPDATE_CHATROOM,
                re.compile(f"(?P<session_id>[\w|=]+)::{CommandHandler.UPDATE_CHATROOM}::(?P<contact>\w+)"),
                MessengerServer.update_chatroom, self)
        ]


    def show(self):
        for i, item in enumerate(CommandHandler().items):
            print(f"{i + 1}. {item.text}")

    def parse(command):
        for item in CommandHandler().commands:
            item: Command
            if (match := item.regex.match(command)):
                return item.handler, match.groupdict().values()
        return Command.invalid_command


class Command:
    def __init__(self, text: str, regex: str, handler, menu) -> None:
        self.menu = menu
        self.text = text
        self.regex = regex
        self.handler = handler

    def invalid_command(self):
        print("Invalid Command")