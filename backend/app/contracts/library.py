from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol


class InterestCatalogPort(Protocol):
    """Read-only catalog of library interest options for other bounded contexts."""

    async def all_interest_option_ids_exist(self, interest_ids: Sequence[str]) -> bool:
        """True iff every distinct id exists in `library_interest_option`. Empty → True."""
        ...

    async def labels_for_interest_ids(self, interest_ids: Sequence[str]) -> dict[str, str]:
        """id → label for rows that exist; unknown ids are omitted."""
        ...
