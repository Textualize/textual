"""

Containers to implement caching.

These are used in Textual to avoid recalculating expensive operations, such as rendering.

"""

from __future__ import annotations

from typing import Dict, Generic, KeysView, TypeVar, overload

CacheKey = TypeVar("CacheKey")
CacheValue = TypeVar("CacheValue")
DefaultValue = TypeVar("DefaultValue")

__all__ = ["LRUCache", "FIFOCache"]


class LRUCache(Generic[CacheKey, CacheValue]):
    """
    A dictionary-like container with a maximum size.

    If an additional item is added when the LRUCache is full, the least
    recently used key is discarded to make room for the new item.

    The implementation is similar to functools.lru_cache, which uses a (doubly)
    linked list to keep track of the most recently used items.

    Each entry is stored as [PREV, NEXT, KEY, VALUE] where PREV is a reference
    to the previous entry, and NEXT is a reference to the next value.

    Note that stdlib's @lru_cache is implemented in C and faster! It's best to use
    @lru_cache where you are caching things that are fairly quick and called many times.
    Use LRUCache where you want increased flexibility and you are caching slow operations
    where the overhead of the cache is a small fraction of the total processing time.
    """

    __slots__ = [
        "_maxsize",
        "_cache",
        "_full",
        "_head",
        "hits",
        "misses",
    ]

    def __init__(self, maxsize: int) -> None:
        """Initialize a LRUCache.

        Args:
            maxsize: Maximum size of the cache, before old items are discarded.
        """
        self._maxsize = maxsize
        self._cache: Dict[CacheKey, list[object]] = {}
        self._full = False
        self._head: list[object] = []
        self.hits = 0
        self.misses = 0
        super().__init__()

    @property
    def maxsize(self) -> int:
        """int: Maximum size of cache, before new values evict old values."""
        return self._maxsize

    @maxsize.setter
    def maxsize(self, maxsize: int) -> None:
        self._maxsize = maxsize

    def __bool__(self) -> bool:
        return bool(self._cache)

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return f"<LRUCache size={len(self)} maxsize={self._maxsize} hits={self.hits} misses={self.misses}>"

    def grow(self, maxsize: int) -> None:
        """Grow the maximum size to at least `maxsize` elements.

        Args:
            maxsize: New maximum size.
        """
        self.maxsize = max(self.maxsize, maxsize)

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()
        self._full = False
        self._head = []

    def keys(self) -> KeysView[CacheKey]:
        """Get cache keys."""
        # Mostly for tests
        return self._cache.keys()

    def set(self, key: CacheKey, value: CacheValue) -> None:
        """Set a value.

        Args:
            key: Key.
            value: Value.
        """
        link = self._cache.get(key)
        if link is None:
            head = self._head
            if not head:
                # First link references itself
                self._head[:] = [head, head, key, value]
            else:
                # Add a new root to the beginning
                self._head = [head[0], head, key, value]
                # Updated references on previous root
                head[0][1] = self._head  # type: ignore[index]
                head[0] = self._head
            self._cache[key] = self._head

            if self._full or len(self._cache) > self._maxsize:
                # Cache is full, we need to evict the oldest one
                self._full = True
                head = self._head
                last = head[0]
                last[0][1] = head  # type: ignore[index]
                head[0] = last[0]  # type: ignore[index]
                del self._cache[last[2]]  # type: ignore[index]

    __setitem__ = set

    @overload
    def get(self, key: CacheKey) -> CacheValue | None: ...

    @overload
    def get(
        self, key: CacheKey, default: DefaultValue
    ) -> CacheValue | DefaultValue: ...

    def get(
        self, key: CacheKey, default: DefaultValue | None = None
    ) -> CacheValue | DefaultValue | None:
        """Get a value from the cache, or return a default if the key is not present.

        Args:
            key: Key
            default: Default to return if key is not present.

        Returns:
            Either the value or a default.
        """
        link = self._cache.get(key)
        if link is None:
            self.misses += 1
            return default
        if link is not self._head:
            # Remove link from list
            link[0][1] = link[1]  # type: ignore[index]
            link[1][0] = link[0]  # type: ignore[index]
            head = self._head
            # Move link to head of list
            link[0] = head[0]
            link[1] = head
            self._head = head[0][1] = head[0] = link  # type: ignore[index]
        self.hits += 1
        return link[3]  # type: ignore[return-value]

    def __getitem__(self, key: CacheKey) -> CacheValue:
        link = self._cache.get(key)
        if link is None:
            self.misses += 1
            raise KeyError(key)
        if link is not self._head:
            link[0][1] = link[1]  # type: ignore[index]
            link[1][0] = link[0]  # type: ignore[index]
            head = self._head
            link[0] = head[0]
            link[1] = head
            self._head = head[0][1] = head[0] = link  # type: ignore[index]
        self.hits += 1
        return link[3]  # type: ignore[return-value]

    def __contains__(self, key: CacheKey) -> bool:
        return key in self._cache

    def discard(self, key: CacheKey) -> None:
        """Discard item in cache from key.

        Args:
            key: Cache key.
        """
        if key not in self._cache:
            return
        link = self._cache[key]

        # Remove link from list
        link[0][1] = link[1]  # type: ignore[index]
        link[1][0] = link[0]  # type: ignore[index]
        # Remove link from cache

        if self._head[2] == key:
            self._head = self._head[1]  # type: ignore[assignment]
            if self._head[2] == key:  # type: ignore[index]
                self._head = []

        del self._cache[key]
        self._full = False


class FIFOCache(Generic[CacheKey, CacheValue]):
    """A simple cache that discards the first added key when full (First In First Out).

    This has a lower overhead than LRUCache, but won't manage a working set as efficiently.
    It is most suitable for a cache with a relatively low maximum size that is not expected to
    do many lookups.

    """

    __slots__ = [
        "_maxsize",
        "_cache",
        "hits",
        "misses",
    ]

    def __init__(self, maxsize: int) -> None:
        """Initialize a FIFOCache.

        Args:
            maxsize: Maximum size of cache before discarding items.
        """
        self._maxsize = maxsize
        self._cache: dict[CacheKey, CacheValue] = {}
        self.hits = 0
        self.misses = 0

    def __bool__(self) -> bool:
        return bool(self._cache)

    def __len__(self) -> int:
        return len(self._cache)

    def __repr__(self) -> str:
        return (
            f"<FIFOCache maxsize={self._maxsize} hits={self.hits} misses={self.misses}>"
        )

    def clear(self) -> None:
        """Clear the cache."""
        self._cache.clear()

    def keys(self) -> KeysView[CacheKey]:
        """Get cache keys."""
        # Mostly for tests
        return self._cache.keys()

    def set(self, key: CacheKey, value: CacheValue) -> None:
        """Set a value.

        Args:
            key: Key.
            value: Value.
        """
        if key not in self._cache and len(self._cache) >= self._maxsize:
            for first_key in self._cache:
                self._cache.pop(first_key)
                break
        self._cache[key] = value

    __setitem__ = set

    @overload
    def get(self, key: CacheKey) -> CacheValue | None: ...

    @overload
    def get(
        self, key: CacheKey, default: DefaultValue
    ) -> CacheValue | DefaultValue: ...

    def get(
        self, key: CacheKey, default: DefaultValue | None = None
    ) -> CacheValue | DefaultValue | None:
        """Get a value from the cache, or return a default if the key is not present.

        Args:
            key: Key
            default: Default to return if key is not present.

        Returns:
            Either the value or a default.
        """
        try:
            result = self._cache[key]
        except KeyError:
            self.misses += 1
            return default
        else:
            self.hits += 1
            return result

    def __getitem__(self, key: CacheKey) -> CacheValue:
        try:
            result = self._cache[key]
        except KeyError:
            self.misses += 1
            raise KeyError(key) from None
        else:
            self.hits += 1
            return result

    def __contains__(self, key: CacheKey) -> bool:
        return key in self._cache
