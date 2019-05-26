import typing

from flask import Flask


class Extension:
    def __init__(self, app: typing.Optional[Flask] = None):
        self.app = app
        self.init_app(self.app) if self.app else None

    def init_app(self, app: Flask):
        app.extensions[self.__class__.__name__.lower().replace("extension", "")] = self
