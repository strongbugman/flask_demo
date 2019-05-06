import typing

from flask import Flask


class Extension:
    def __init__(self):
        self.app: typing.Optional[Flask] = None

    def init_app(self, app: Flask):
        self.app = app
        self.startup()

    def startup(self):
        pass
