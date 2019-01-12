
class User:
    def __init__(self, id):
        self.id = id
        self.online = False
        self.messages = []

    def add_message(self, message):
        self.messages.append(message)

