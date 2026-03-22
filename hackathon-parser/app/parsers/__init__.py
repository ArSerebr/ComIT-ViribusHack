"""Парсеры внешних источников хакатонов."""

from app.parsers.base import RawHackathon
from app.parsers.cups_online import CupsOnlineParser
from app.parsers.hacklist import HacklistParser
from app.parsers.networkly import NetworklyParser

__all__ = ["RawHackathon", "HacklistParser", "CupsOnlineParser", "NetworklyParser", "get_parsers"]


def get_parsers() -> list:
    return [HacklistParser(), CupsOnlineParser(), NetworklyParser()]
