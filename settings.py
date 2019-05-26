import os
import logging

ENV = os.environ.get("FLASK_ENV", default="production")  # same with flask run
DEBUG = os.environ.get("FLASK_ENV", default="true") in ("t", "true")

PROJECT_NAME = "flask_demo"

# extensions
DB_URL = f"mysql://root:letmein@127.0.0.1/{PROJECT_NAME}?charset=utf8mb4"
DB_CONFIG = dict(echo=True, echo_pool=True, pool_size=10)

APIMAN_TEMPLATE = "./docs/template.yml"
APIMAN_CONFIG = {"title": "Flask demo API manunal"}

if ENV == "testing":
    logging.basicConfig(level=logging.DEBUG)
    DB_URL = DB_URL.replace(PROJECT_NAME, PROJECT_NAME + "_test")
elif ENV == "development":
    logging.basicConfig(level=logging.DEBUG)
else:
    DEBUG = False
    DB_CONFIG["echo"] = False
    logging.basicConfig(level=logging.WARNING)
