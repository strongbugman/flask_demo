from flask.views import MethodView
from flask import request, Response

from app import models as m, utils, exceptions as excs, extensions as exts


class CatView(MethodView):
    def get(self):
        """
        summary: Get single cat
        tags:
        - cat
        parameters:
        - name: id
          in: query
          required: True
          schema:
            type: integer
        responses:
          "200":
            description: OK
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Cat'
          "404":
            description: Not found
        """
        return utils.JSONResponse(
            m.Cat.get_dict(utils.parse_id(request.args.get("id")))
        )

    def put(self):
        """
        summary: Update single cat
        tags:
        - cat
        requestBody:
          required: true
          content:
            application/json:
              schema:
                type: object
                required:
                - id
                properties:
                  name:
                    type: string
                    maxLength: 32
                    description: naming cat
                  age:
                    type: integer
                  id:
                    type: integer
                    minimum: 1
        responses:
          "201":
            description: OK
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Cat'
          "404":
            description: Not found
        """
        data = utils.get_json(request)
        cat = m.Cat(**data)
        if not cat.id:
            raise excs.InvalidId()
        else:
            cat.save()
            return utils.JSONResponse(cat.dict())

    def delete(self):
        """
        summary: Delete single cat
        tags:
        - cat
        parameters:
        - name: id
          in: query
          required: True
          schema:
            type: integer
        responses:
          "204":
            description: OK
          "404":
            description: Not found
        """
        m.Cat.delete(utils.parse_id(request.args.get("id")))
        return Response(status=204)


class CatsView(MethodView):
    def get(self):
        """
        summary: Get all cats
        tags:
        - cats
        parameters:
        - name: page
          in: query
          required: False
          schema:
            type: integer
            default: 1
            minimum: 1
        - name: count
          in: query
          required: False
          schema:
            type: integer
            default: 20
            maximum: 40
            minimum: 1
        responses:
          "200":
            description: OK
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/Cats'
        """
        page, count = utils.parse_paginate(request)
        return utils.JSONResponse(
            {
                "objects": m.Cat.list_dict(page=page, count=count),
                "page": page,
                "count": count,
            }
        )

    @exts.apiman.from_file("./docs/cats_post.yml")
    def post(self):
        data = utils.get_json(request)
        cat = m.Cat(**data)
        cat.save()
        return utils.JSONResponse(cat.dict(), status=201)
