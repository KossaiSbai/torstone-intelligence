"""SQLAlchemy database instance and base model class"""
from abc import ABC
import json
from typing import Any, Optional, Type, TypeVar
from langchain_core.load import Serializable, load
from langchain_core.documents import Document
from langchain_core.load.serializable import SerializedConstructor, SerializedNotImplemented
from sqlalchemy import TypeDecorator
from sqlalchemy import Text
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from typing_extensions import override
from flask_sqlalchemy import SQLAlchemy

__all__ = ["db", "Base"]


X = TypeVar("X", bound=Serializable)

class Wrapper(TypeDecorator[X], ABC):
    """A wrapper for storing documents in the database"""
    impl = Text

    cache_ok = True

    @override
    def process_bind_param(self, value: Any, dialect: Any) -> str:
        if not isinstance(value, Serializable):
            raise ValueError(f"Expected Serializable, got {type(value)}")
        json_dict: SerializedConstructor | SerializedNotImplemented = value.to_json()
        assert isinstance(json_dict, dict)
        return json.dumps(json_dict)

    @override
    def process_result_value(self, value: Any | None, dialect: Any) -> Optional[X]:
        if value is None:
            return None
        json_dict = json.loads(value)
        return load(json_dict)

    @override
    def process_literal_param(self, value: Any, dialect: Any) -> str:
        return self.process_bind_param(value, dialect)

    @property
    def python_type(self) -> Type[X]:
        raise NotImplementedError


T = TypeVar("T", bound=Serializable)


def serializable_wrapper(wrapped_type: Type[T])  -> type[Wrapper[T]]:
    """Create a wrapper for a serializable type"""

    class WrapperI(Wrapper[T]):
        """A wrapper for storing documents in the database"""
        @property
        def python_type(self) -> Type[T]:
            return wrapped_type

    return WrapperI


DocumentWrapper: type[Wrapper[Document]] = serializable_wrapper(Document)


class Base(DeclarativeBase, MappedAsDataclass):
    """Base class for all database models"""

Base.registry.type_annotation_map.update(
    {
        Document: DocumentWrapper,
    }
)

db = SQLAlchemy(model_class=Base)
