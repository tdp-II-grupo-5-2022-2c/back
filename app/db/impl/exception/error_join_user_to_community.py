class ErrorJoinUserToCommunity(Exception):
    def __init__(self, message="Can't not join user in community"):
        self.message = message
        super().__init__(self.message)
