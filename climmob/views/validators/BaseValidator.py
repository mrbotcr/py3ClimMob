class BaseValidator:
    def __init__(self, request):
        self.request = request

    def run(self):
        raise NotImplementedError
