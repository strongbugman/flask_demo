import typing
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.result import RowProxy
from sqlalchemy.sql import text
from sqlalchemy.sql.elements import TextClause

from .base import Extension
from app import exceptions as excs


class DBExtension(Extension):
    def __init__(self, db_url: str, config: typing.Dict[str, typing.Any]):
        super().__init__()
        self.engine: Engine = create_engine(db_url, **config)

    def execute(self, sql: TextClause, **params) -> None:
        self.engine.execute(sql, **params)

    def fetch(self, sql: TextClause, **params) -> typing.List[RowProxy]:
        res = self.engine.execute(sql, **params).fetchall()
        if not res:
            raise excs.NotFound()
        return res

    def insert(self, table: str, data: typing.Dict[str, typing.Any]) -> int:
        sql = text(
            "INSERT INTO {table:s} ({columns:s}) VALUES ({values:s});".format(
                table=table.lower(),
                columns=", ".join(data),
                values=", ".join([f":{k}" for k in data]),
            )
        )

        with self.engine.begin():
            self.execute(sql, **data)
            return self.fetch("SELECT LAST_INSERT_ID()")[0][0]

    def update(
        self, table: str, data: typing.Dict[str, typing.Any], **condition: typing.Any
    ):
        assert data

        sql = text(
            "UPDATE {table:s} SET {data:s} WHERE {condition:s};".format(
                table=table.lower(),
                data=", ".join((f"{k}=:{k}" for k in data)),
                condition=", ".join((f"{k}=:{k}" for k in condition)),
            )
        )
        self.execute(sql, **data, **condition)

    def count(self, table: str, **condition: typing.Any) -> int:
        sql = text(
            f"SELECT COUNT(*) FROM {table} WHERE {', '.join((f'{k}=:{k}' for k in condition))};"
        )

        return self.fetch(sql)[0][0]

    def transaction(self, f: typing.Callable) -> typing.Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            with self.engine.begin():
                f(*args, **kwargs)

        return wrapper
