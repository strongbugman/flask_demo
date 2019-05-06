import typing
import enum
from collections import Sequence
from functools import wraps
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.result import ResultProxy, RowProxy

from .base import Extension


Field = typing.Union[int, float, bool, str, None, enum.Enum, datetime]


class DBExtension(Extension):
    INSERT_SQL = "INSERT INTO {table:s} ({columns:s}) VALUES ({values:s});"
    UPDATE_SQL = "UPDATE {table:s} SET {data:s} WHERE {condition:s};"
    INJECTION_CHARS = ("'", '"', "`", "\\")

    def __init__(self, db_url: str, config: typing.Dict[str, typing.Any]):
        super().__init__()
        self.engine: Engine = create_engine(db_url, **config)

    @classmethod
    def parse(cls, value: Field) -> str:
        """Parse value to str for making sql string, eg: False -> '0'
        """
        if isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, str):
            for c in cls.INJECTION_CHARS:
                value = value.replace(c, "\\" + c)
            return "'{:s}'".format(value)
        elif value is None:
            return "NULL"
        elif isinstance(value, Sequence):
            return f"'{{{','.join(cls.parse(v) for v in value)}}}'"
        elif isinstance(value, enum.Enum):
            return str(value.value)
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, datetime):
            return f"'{value}'"
        else:
            raise ValueError(f"Value {value.__class__}-{value} is not support!")

    def execute(self, sql: str) -> None:
        self.engine.execute(sql)

    def fetch(self, sql) -> typing.List[RowProxy]:
        res: ResultProxy = self.engine.execute(sql)
        return res.fetchall()

    def insert(self, table: str, data: typing.Dict[str, Field]) -> int:
        assert data

        keys = data.keys()
        values = data.values()
        sql = self.INSERT_SQL.format(
            table=table.lower(),
            columns=", ".join(list(keys)),
            values=", ".join([f"{self.parse(value)}" for value in values]),
        )

        with self.engine.begin():
            self.execute(sql)
            return self.fetch("SELECT LAST_INSERT_ID()")[0][0]

    def update(self, table: str, data: typing.Dict[str, Field], **condition: Field):
        assert data

        sql = self.UPDATE_SQL.format(
            table=table.lower(),
            data=", ".join((f"{k}={self.parse(v)}" for k, v in data.items())),
            condition=", ".join((f"{k}={self.parse(v)}" for k, v in condition.items())),
        )
        self.execute(sql)

    def count(self, table: str, **condition: Field) -> int:
        sql = f"SELECT COUNT(*) FROM {table} WHERE {', '.join((f'{k}={self.parse(v)}' for k, v in condition.items()))};"

        return self.fetch(sql)[0][0]

    def transaction(self, f: typing.Callable) -> typing.Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            with self.engine.begin():
                f(*args, **kwargs)

        return wrapper
