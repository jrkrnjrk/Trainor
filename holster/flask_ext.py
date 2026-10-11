from flask import Flask

class Holster:
    def __init__(self, app=None):
        self.app = app or Flask(__name__)
    def __getattr__(self, name):
        return getattr(self.app, name)
