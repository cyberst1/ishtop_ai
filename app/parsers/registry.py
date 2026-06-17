"""
Central parser registry.

Active sources (Uzbekistan-focused):
  • hh.uz          — HeadHunter API (area=97). May be 403 from cloud IPs;
                      works from residential / VPS in UZ.
  • olx.uz         — public HTML
  • osonish.uz     — public JSON API
  • ish-kerak.uz   — public HTML
  • Telegram       — preview-page scraping of public channels

Disabled (returned irrelevant / global results):
  • Indeed RSS    — global jobs, poor UZ coverage
  • LinkedIn      — corporate-only, not local
  • Jooble        — needs paid API key

To re-enable a disabled parser, uncomment its line below.
"""
from __future__ import annotations

from app.parsers.base import BaseParser
from app.parsers.hh_uz import HhUzParser
from app.parsers.olx_uz import OlxUzParser
from app.parsers.osonish_uz import OsonishUzParser
from app.parsers.ishkerak_uz import IshKerakParser
from app.parsers.telegram_channels import TelegramChannelsParser
# from app.parsers.jooble import JoobleParser
# from app.parsers.linkedin import LinkedInParser
# from app.parsers.indeed import IndeedParser


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: list[BaseParser] = [
            HhUzParser(),
            OlxUzParser(),
            OsonishUzParser(),
            IshKerakParser(),
            TelegramChannelsParser(),
        ]

    def all(self) -> list[BaseParser]:
        return list(self._parsers)
