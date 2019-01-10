class ApiMessage:
    def __init__(self, msg):
        self.msg = msg

    def dict(self):
        return self.__dict__
