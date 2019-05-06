from flask import Flask

import settings

from .api import api
from .extensions import EXTENSIONS


app = Flask(settings.PROJECT_NAME)


@app.route(f"/{settings.PROJECT_NAME}/health/", methods=("GET",))
def health():
    return "OK"


# blueprints
app.register_blueprint(api)


# extensions
for ext in EXTENSIONS:
    ext.init_app(app)
