class History:

    def __init__(self):
        self._messages = []
        self.owner = None

    def add(self, message, _from=None):
        self._messages.append(message)

    def messages(self):
        return self._messages  # TODO: make message roles based on the owner

    def encode(self):
        return [msg.encode() for msg in self._messages]

    def set_owner(self, owner):
        self.owner = owner
