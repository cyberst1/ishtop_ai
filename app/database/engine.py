"""
Async SQLite engine + connection pool.
Use parameterized queries ONLY (SQLi-proof).
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

import aiosqlite

from app.config import settings
from app.utils.logger import logger


class Database:
    """Thin wrapper around aiosqlite with a single shared connection (SQLite is fine for this)."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._conn: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        if self._conn is None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = await aiosqlite.connect(self.path)
            self._conn.row_factory = aiosqlite.Row
            await self._conn.execute("PRAGMA foreign_keys = ON;")
            await self._conn.execute("PRAGMA journal_mode = WAL;")
            await self._conn.commit()
            logger.info("db.connected", extra={"path": str(self.path)})

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def init_schema(self) -> None:
        schema = Path(__file__).parent / "schema.sql"
        sql = schema.read_text(encoding="utf-8")
        assert self._conn
        await self._conn.executescript(sql)
        await self._conn.commit()
        logger.info("db.schema_initialized")

    @asynccontextmanager
    async def cursor(self):
        assert self._conn, "Database not connected"
        async with self._lock:
            cur = await self._conn.cursor()
            try:
                yield cur
                await self._conn.commit()
            except Exception:
                await self._conn.rollback()
                raise
            finally:
                await cur.close()

    async def execute(self, sql: str, params: tuple = ()) -> None:
        async with self.cursor() as cur:
            await cur.execute(sql, params)

    async def fetchone(self, sql: str, params: tuple = ()) -> Optional[aiosqlite.Row]:
        async with self.cursor() as cur:
            await cur.execute(sql, params)
            return await cur.fetchone()

    async def fetchall(self, sql: str, params: tuple = ()) -> list[aiosqlite.Row]:
        async with self.cursor() as cur:
            await cur.execute(sql, params)
            return list(await cur.fetchall())


_db: Optional[Database] = None


def get_db() -> Database:
    global _db
    if _db is None:
        _db = Database(settings.db_path)
    return _db


async def main() -> None:
    """python -m app.database.engine — initialise the DB."""
    db = get_db()
    await db.connect()
    await db.init_schema()
    print(f"✅ DB initialised at {db.path}")
    await db.close()


if __name__ == "__main__":
    asyncio.run(main())
