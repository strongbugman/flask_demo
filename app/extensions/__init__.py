import settings
from .database import DBExtension

db = DBExtension(settings.DB_URL, settings.DB)

EXTENSIONS = (db,)
