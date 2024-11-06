from typing import Iterable, Callable, TypeVar


T = TypeVar('T')

def partition(pred: Callable[[T], bool], iterable: Iterable[T]) -> tuple[list[T], list[T]]:
    """Use a predicate to partition entries into matching and non-matching entries"""
    ins = []
    outs = []
    for item in iterable:
        if pred(item):
            ins.append(item)
        else:
            outs.append(item)
    return ins, outs
