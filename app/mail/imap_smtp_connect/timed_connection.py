import time


class TimedConnection:
    def __init__(self, connection):
        self.connection = connection
        self.last_used = time.time()

    def is_expired(self, expiry_seconds: int) -> bool:
        return (time.time() - self.last_used) > expiry_seconds
