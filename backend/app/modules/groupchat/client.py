"""HTTP client for QmsgCore API."""

from __future__ import annotations

import uuid

import httpx

from app.config import get_settings


class QmsgCoreClient:
    def __init__(self, base_url: str | None = None) -> None:
        self._base = (base_url or get_settings().qmsg_core_base_url).rstrip("/")

    async def fetch_token(self, user_id: uuid.UUID) -> str:
        """Get QmsgCore JWT for the given user. Returns access_token."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base}/v1/auth/token",
                json={"uid": str(user_id)},
                headers={"Content-Type": "application/json"},
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return str(data["access_token"])

    async def create_group(self, access_token: str, name: str) -> str:
        """Create a group in QmsgCore. Caller becomes owner. Returns group_id."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base}/v1/groups",
                json={"name": name},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=10.0,
            )
            resp.raise_for_status()
            data = resp.json()
            return str(data["id"])

    async def add_member(self, access_token: str, group_id: str, user_id: uuid.UUID) -> None:
        """Add a member to a group. Requires owner or admin role."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base}/v1/groups/{group_id}/members",
                json={"user_id": str(user_id)},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=10.0,
            )
            resp.raise_for_status()

    async def delete_group(self, access_token: str, group_id: str) -> None:
        """Delete a group. Requires owner role."""
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{self._base}/v1/groups/{group_id}",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0,
            )
            resp.raise_for_status()
