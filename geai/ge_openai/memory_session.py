from dataclasses import dataclass, field
from typing import Generic, TypeVar, List

TResponseInputItem = TypeVar("TResponseInputItem")


@dataclass
class InMemorySession(Generic[TResponseInputItem]):
    session_id: str
    _items: List[TResponseInputItem] = field(default_factory=list)

    async def get_items(self, limit: int | None = None) -> list[TResponseInputItem]:
        if limit is None or limit >= len(self._items):
            return list(self._items)
        # latest N items in chronological order
        return self._items[-limit:]

    async def add_items(self, items: list[TResponseInputItem]) -> None:
        self._items.extend(items)

    async def pop_item(self) -> TResponseInputItem | None:
        if not self._items:
            return None
        return self._items.pop()

    async def clear_session(self) -> None:
        self._items.clear()
