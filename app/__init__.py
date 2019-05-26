from flask import Flask

import settings

from .api import api
from .extensions import EXTENSIONS


app = Flask(settings.PROJECT_NAME)
app.config.from_object(settings)


@app.route(f"/health/", methods=("GET",))
def health():
    """
    summary: Service health
    tags:
    - health
    responses:
        200:
            description: OK
    """
    return "OK"


# blueprints
app.register_blueprint(api)


# extensions
for ext in EXTENSIONS:
    ext.init_app(app)
