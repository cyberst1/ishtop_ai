"""Central registry — single source of truth for parser instantiation."""
from __future__ import annotations

from app.parsers.base import BaseParser
from app.parsers.hh_uz import HhUzParser
from app.parsers.olx_uz import OlxUzParser
from app.parsers.jooble import JoobleParser
from app.parsers.linkedin import LinkedInParser
from app.parsers.indeed import IndeedParser
from app.parsers.telegram_channels import TelegramChannelsParser


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: list[BaseParser] = [
            HhUzParser(),
            OlxUzParser(),
            JoobleParser(),
            LinkedInParser(),
            IndeedParser(),
            TelegramChannelsParser(),
        ]

    def all(self) -> list[BaseParser]:
        return list(self._parsers)
