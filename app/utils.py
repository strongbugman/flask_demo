import typing
from json import JSONDecodeError
import enum

from flask import Request, Response
import ujson

from . import exceptions


def get_sign(func: typing.Callable, *args, **kwargs) -> str:
    return f"{func.__name__}_{args}_{kwargs}".replace(" ", "").replace("'", "")


def get_json(req: Request) -> typing.Dict:
    try:
        if not req.is_json:
            raise exceptions.InvalidJson("Json type required!")
        else:
            return ujson.loads(req.data)
    except (JSONDecodeError, ValueError) as e:
        raise exceptions.InvalidJson(str(e)) from e


def parse_integer(num: typing.Union[str, int]) -> int:
    if isinstance(num, str):
        if not num.isdecimal():
            raise exceptions.InvalidId("Filed is not a number!")
        else:
            num = int(num)

    return num


def parse_id(_id: typing.Union[str, int, None]) -> int:
    if not _id:
        raise exceptions.InvalidId("Miss fields!")

    _id = parse_integer(_id)

    if _id < 0:
        raise exceptions.InvalidId("Filed small than zero!")
    else:
        return _id


def parse_paginate(req: Request):
    page = parse_id(req.args.get("page", 1))
    count = parse_id(req.args.get("count", 20))

    if count > 40:
        raise exceptions.InvalidException("Field is bigger than 40")

    return page, count


class JSONResponse(Response):
    def __init__(self, data: typing.Any, status=200):
        for k in data.keys():
            if isinstance(data[k], enum.Enum):
                data[k] = data[k].name

        super().__init__(
            ujson.dumps(data, ensure_ascii=False).encode("utf-8"),
            status=status,
            mimetype="application/json",
        )
