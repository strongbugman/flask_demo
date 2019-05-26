import typing
from datetime import datetime

from pydantic import BaseModel as _BaseModel, ValidationError
from pydantic.error_wrappers import ErrorWrapper
from sqlalchemy.sql import text

from . import extensions as exts


M = typing.TypeVar("M", bound="Base")


class Base(_BaseModel):
    __db_define__ = f"""
CREATE TABLE base (
    id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
"""

    id: int = 0
    created_at: typing.Optional[datetime] = None
    updated_at: typing.Optional[datetime] = None

    def __init__(self, **data: typing.Any):
        super().__init__(**data)

        self.validate_all()

    def validate_all(self) -> None:
        errors = self.get_validate_errors()
        if errors:
            raise ValidationError(
                [ErrorWrapper(ValueError(e), loc=f) for f, e in errors.items()]
            )

    def get_validate_errors(self) -> typing.Dict[str, str]:
        errors: typing.Dict[str, str] = {}
        if self.id < 0:
            errors["id"] = "small than zero!"

        return errors

    def save(self) -> None:
        self.validate_all()

        if self.id != 0:
            data = self.dict(exclude={"created_at", "updated_at", "id"})
            exts.db.update(self.__class__.__name__, data, id=self.id)
        else:
            self.created_at = self.updated_at = datetime.now()
            data = self.dict(exclude={"id"})
            self.id = exts.db.insert(self.__class__.__name__, data)

    @classmethod
    def get(cls: typing.Type[M], _id: int) -> M:
        result = (
            exts.db.fetch(
                text(
                    f"SELECT {','.join(cls.__fields__.keys())} FROM {cls.__name__.lower()} WHERE id=:_id;"
                ),
                _id=_id,
            )
        )[0]

        return cls(**result)

    @classmethod
    def get_dict(cls: typing.Type[M], _id: int) -> typing.Dict[str, typing.Any]:
        return cls.get(_id).dict()

    @classmethod
    def delete(cls, _id: int) -> None:
        exts.db.execute(
            text(f"DELETE FROM {cls.__name__.lower()} WHERE id=:_id"), _id=_id
        )

    @classmethod
    def list(cls: typing.Type[M], page: int = 1, count: int = 20) -> typing.List[M]:
        results = exts.db.fetch(
            text(
                f"SELECT {','.join(cls.__fields__.keys())} FROM {cls.__name__.lower()} ORDER BY id ASC LIMIT :count OFFSET :offset"
            ),
            count=count,
            offset=(page - 1) * count,
        )
        return [cls(**result) for result in results]

    @classmethod
    def list_dict(
        cls: typing.Type[M], page: int = 1, count: int = 20
    ) -> typing.List[typing.Dict[str, typing.Any]]:
        return [obj.dict() for obj in cls.list(page=page, count=count)]


class Cat(Base):
    __db_define__ = """
CREATE TABLE cat (
    id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    name VARCHAR(32) NOT NULL,
    age INTEGER DEFAULT 0 NOT NULL
);
"""

    name: str
    age: int = 0

    def get_validate_errors(self) -> typing.Dict[str, str]:
        errors = super().get_validate_errors()

        if self.age < 0:
            errors["age"] = "small than zero!"
        if len(self.name) > 32:
            errors["name"] = "length is too long!(Limit to 32)"
        return errors


MODELS = {Cat}


for m_cls in MODELS:
    exts.apiman.add_schema(m_cls.__name__, m_cls.schema())
    exts.apiman.add_schema(
        f"{m_cls.__name__}s",
        {
            "type": "object",
            "properties": {
                "objects": {
                    "type": "array",
                    "items": {"$ref": f"#/components/schemas/{m_cls.__name__}"},
                },
                "page": {"type": "integer"},
                "count": {"type": "integer"},
            },
        },
    )
