"""

A LRU (Least Recently Used) Cache container.

Use when you want to cache slow operations and new keys are a good predictor
of subsequent keys.

Note that stdlib's @lru_cache is implemented in C and faster! It's best to use
@lru_cache where you are caching things that are fairly quick and called many times.
Use LRUCache where you want increased flexibility and you are caching slow operations
where the overhead of the cache is a small fraction of the total processing time.  

"""

from threading import Lock
from typing import (
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
    overload,
)

CacheKey = TypeVar("CacheKey")
CacheValue = TypeVar("CacheValue")
DefaultValue = TypeVar("DefaultValue")


class LRUCache(Generic[CacheKey, CacheValue]):
    """
    A dictionary-like container with a maximum size.

    If an additional item is added when the LRUCache is full, the least
    recently used key is discarded to make room for the new item.

    The implementation is similar to functools.lru_cache, which uses a (doubly)
    linked list to keep track of the most recently used items.

    Each entry is stored as [PREV, NEXT, KEY, VALUE] where PREV is a reference
    to the previous entry, and NEXT is a reference to the next value.

    """

    def __init__(self, maxsize: int) -> None:
        self.maxsize = maxsize
        self.cache: Dict[CacheKey, List[object]] = {}
        self.full = False
        self.head: List[object] = []
        self._lock = Lock()
        super().__init__()

    def __len__(self) -> int:
        return len(self.cache)

    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            self.cache.clear()
            self.full = False
            self.head = []

    def set(self, key: CacheKey, value: CacheValue) -> None:
        """Set a value.

        Args:
            key (CacheKey): Key.
            value (CacheValue): Value.
        """
        with self._lock:
            link = self.cache.get(key)
            if link is None:
                head = self.head
                if not head:
                    # First link references itself
                    self.head[:] = [self.head, self.head, key, value]
                else:
                    # Add a new root to the beginning
                    self.head = [head[0], head, key, value]
                    # Updated references on previous root
                    head[0][1] = self.head  # type: ignore[index]
                    head[0] = self.head
                self.cache[key] = self.head

                if self.full or len(self.cache) > self.maxsize:
                    # Cache is full, we need to evict the oldest one
                    self.full = True
                    head = self.head
                    last = head[0]
                    last[0][1] = head  # type: ignore[index]
                    head[0] = last[0]  # type: ignore[index]
                    del self.cache[last[2]]  # type: ignore[index]

    __setitem__ = set

    @overload
    def get(self, key: CacheKey) -> Optional[CacheValue]:
        ...

    @overload
    def get(
        self, key: CacheKey, default: DefaultValue
    ) -> Union[CacheValue, DefaultValue]:
        ...

    def get(
        self, key: CacheKey, default: Optional[DefaultValue] = None
    ) -> Union[CacheValue, Optional[DefaultValue]]:
        """Get a value from the cache, or return a default if the key is not present.

        Args:
            key (CacheKey): Key
            default (Optional[DefaultValue], optional): Default to return if key is not present. Defaults to None.

        Returns:
            Union[CacheValue, Optional[DefaultValue]]: Either the value or a default.
        """
        link = self.cache.get(key)
        if link is None:
            return default
        with self._lock:
            if link is not self.head:
                # Remove link from list
                link[0][1] = link[1]  # type: ignore[index]
                link[1][0] = link[0]  # type: ignore[index]
                head = self.head
                # Move link to head of list
                link[0] = head[0]
                link[1] = head
                head[0][1] = link  # type: ignore[index]
                head[0] = link
                # Update root
                self.head = link
            return link[3]  # type: ignore[return-value]

    def __getitem__(self, key: CacheKey) -> CacheValue:
        link = self.cache[key]
        with self._lock:
            if link is not self.head:
                link[0][1] = link[1]  # type: ignore[index]
                link[1][0] = link[0]  # type: ignore[index]
                head = self.head
                link[0] = head[0]
                link[1] = head
                head[0][1] = link  # type: ignore[index]
                head[0] = link
                self.head = link
            return link[3]  # type: ignore[return-value]

    def __contains__(self, key: CacheKey) -> bool:
        return key in self.cache
