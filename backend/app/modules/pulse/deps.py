"""Pulse module dependencies."""

from __future__ import annotations

from app.modules.pulse.client import PulseCoreClient
from app.modules.pulse.service import PulseService
from fastapi import Depends


def get_pulse_client() -> PulseCoreClient:
    return PulseCoreClient()


def get_pulse_service(
    client: PulseCoreClient = Depends(get_pulse_client),
) -> PulseService:
    return PulseService(client)
