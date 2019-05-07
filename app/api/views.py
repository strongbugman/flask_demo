from flask.views import MethodView
from flask import request, Response

from app import models as m, utils, exceptions as excs


class CatView(MethodView):
    def get(self):
        return utils.JSONResponse(
            m.Cat.get_dict(utils.parse_id(request.args.get("id")))
        )

    def put(self):
        data = utils.get_json(request)
        cat = m.Cat(**data)
        if not cat.id:
            raise excs.InvalidId()
        else:
            cat.save()
            return utils.JSONResponse(cat.dict())

    def delete(self):
        m.Cat.delete(utils.parse_id(request.args.get("id")))
        return Response(status=204)


class CatsView(MethodView):
    def get(self):
        page, count = utils.parse_paginate(request)
        return utils.JSONResponse(
            {
                "objects": m.Cat.list_dict(page=page, count=count),
                "page": page,
                "count": count,
            }
        )

    def post(self):
        data = utils.get_json(request)
        cat = m.Cat(**data)
        cat.save()
        return utils.JSONResponse(cat.dict(), status=201)
