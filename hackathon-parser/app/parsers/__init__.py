"""Парсеры внешних источников хакатонов."""

from app.parsers.base import RawHackathon
from app.parsers.hacklist import HacklistParser
from app.parsers.cups_online import CupsOnlineParser

__all__ = ["RawHackathon", "HacklistParser", "CupsOnlineParser", "get_parsers"]


def get_parsers() -> list:
    return [HacklistParser(), CupsOnlineParser()]
