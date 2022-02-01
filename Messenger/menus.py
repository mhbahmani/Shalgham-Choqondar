from meta import SingletonMeta

import re


class CommandHandler(metaclass=SingletonMeta):
    SIGNUP = "signup"
    LOGIN = "login"

    def __init__(self) -> None:
        from Messenger.messenger import MessengerServer
        self.commands = [
            Command(
                CommandHandler.SIGNUP, re.compile(f"(?P<session_id>[\w|=]+)::{CommandHandler.SIGNUP}"),
                MessengerServer.signup, self),
            Command(
                CommandHandler.LOGIN, re.compile(f"(?P<session_id>[\w|=]+)::{CommandHandler.LOGIN}"),
                MessengerServer.login, self)
        ]

    def show(self):
        for i, item in enumerate(CommandHandler().items):
            print(f"{i + 1}. {item.text}")

    def parse(command):
        for item in CommandHandler().items:
            item: Command
            if (match := item.regex.match(command)):
                print(match)
                return item.handler
        return Command.invalid_command


class Command:
    def __init__(self, text: str, regex: str, handler, menu) -> None:
        self.text = text
        self.regex = regex
        self.handler = handler
        self.menu = menu

    def invalid_command(self):
        print("Invalid Command")