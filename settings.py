import os
import logging

ENV = os.getenv("FLASK_ENV", "production")

PROJECT_NAME = "flask_demo"

# extensions
DB_URL = f"mysql://root:toor333666@127.0.0.1/{PROJECT_NAME}?charset=utf8mb4"
DB = dict(echo=True, echo_pool=True, pool_size=10)

if ENV == "testing":
    logging.basicConfig(level=logging.DEBUG)
    DB_URL = DB_URL.replace(PROJECT_NAME, PROJECT_NAME + "_test")
elif ENV == "development":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)
