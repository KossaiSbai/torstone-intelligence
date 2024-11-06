from collections.abc import MutableMapping
from contextlib import AbstractContextManager
from io import TextIOBase
import os
from types import TracebackType
from typing import TYPE_CHECKING, Any
import json

if TYPE_CHECKING:
    from _typeshed import FileDescriptorOrPath


__all__ = ['JsonDict']


class JsonDict(AbstractContextManager, MutableMapping):
    """A dictionary with a json backing"""
    _data: dict
    _file: TextIOBase
    _file_descriptor: 'FileDescriptorOrPath'

    def __init__(self, file_descriptor: 'FileDescriptorOrPath') -> None:
        super().__init__()
        self._file = None
        self._data = None
        self._file_descriptor = file_descriptor

    def __enter__(self) -> 'JsonDict':
        if os.path.exists(self._file_descriptor):
            with open(self._file_descriptor, 'rt', encoding='utf-8') as f:
                self._data = json.load(f)
        else:
            self._data = {}
        self._file = open(self._file_descriptor, 'wt', encoding='utf-8').__enter__()
        return super().__enter__()

    def __exit__(
        self,
        __exc_type: type[BaseException] | None,
        __exc_value: BaseException | None,
        __traceback: TracebackType | None
    ) -> bool | None:
        if self._file is not None:
            json.dump(self._data, self._file, indent=4)
            self._file = self._file.__exit__(__exc_type, __exc_value, __traceback)
            self._data = None
        return super().__exit__(__exc_type, __exc_value, __traceback)

    def __getitem__(self, __key: Any) -> Any:
        return self._data.__getitem__(__key)

    def __setitem__(self, __key: Any, __value: Any) -> None:
        return self._data.__setitem__(__key, __value)

    def __delitem__(self, __key: Any) -> None:
        return self._data.__delitem__(__key)

    def __iter__(self) -> Any:
        return self._data.__iter__()

    def __len__(self) -> int:
        return self._data.__len__()
