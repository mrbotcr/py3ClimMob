from pyramid.httpexceptions import HTTPBadRequest


class BaseValidator:
    def __init__(self, view):
        self.view = view
        self._ = view.request.translate

    def run(self):
        raise NotImplementedError

    def float_parse(self, value, name: str):
        try:
            return float(value)
        except ValueError:
            msg = self._("{} must be a number").format(name)
            raise HTTPBadRequest(msg)
