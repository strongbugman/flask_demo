from flask import Blueprint

from .views import CatView, CatsView

api = Blueprint("api", __name__, url_prefix=f"/api")


api.add_url_rule("/cat/", view_func=CatView.as_view(name="cat"))
api.add_url_rule("/cats/", view_func=CatsView.as_view(name="cats"))
