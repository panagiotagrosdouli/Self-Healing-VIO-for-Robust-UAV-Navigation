from collections import deque
from dataclasses import dataclass
from typing import Deque, Generic, Iterable, TypeVar


T = TypeVar('T')


@dataclass
class TemporalTrend:
    first: float
    last: float
    delta: float
    mean: float


class TemporalBuffer(Generic[T]):
    def __init__(self, max_size: int) -> None:
        if max_size <= 0:
            raise ValueError('max_size must be positive')
        self.max_size = max_size
        self._items: Deque[T] = deque(maxlen=max_size)

    def append(self, item: T) -> None:
        self._items.append(item)

    def values(self) -> list[T]:
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)

    @property
    def is_full(self) -> bool:
        return len(self._items) == self.max_size


def compute_trend(values: Iterable[float]) -> TemporalTrend:
    values = list(values)
    if not values:
        return TemporalTrend(first=0.0, last=0.0, delta=0.0, mean=0.0)
    first = values[0]
    last = values[-1]
    mean = sum(values) / len(values)
    return TemporalTrend(first=first, last=last, delta=last - first, mean=mean)
