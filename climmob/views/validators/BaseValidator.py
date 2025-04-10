class BaseValidator:
    def __init__(self, view):
        self.view = view

    def run(self):
        raise NotImplementedError
