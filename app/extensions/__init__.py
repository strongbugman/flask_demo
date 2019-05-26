from apiman.flask import Extension as Apiman

import settings
from .database import DBExtension

db = DBExtension(settings.DB_URL, settings.DB_CONFIG)
apiman = Apiman(settings.APIMAN_TEMPLATE, **settings.APIMAN_CONFIG)

EXTENSIONS = (db, apiman)
