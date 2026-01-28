class APIAuthError(Exception):
    def __init__(self, description: str, status_code: int = 401):
        self.description = description
        self.status_code = status_code
        super().__init__(description)
