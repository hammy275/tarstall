class TarstallHumanReadableError(Exception):

    def __init__(self, message: str):
        super().__init__()
        self.add_note(message)

        self._message = message

    @property
    def message(self) -> str:
        return self._message