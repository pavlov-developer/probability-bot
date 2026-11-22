import aiosqlite
import os

class DataBase:
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = "/data/bot_database.db"
        self.db_path = db_path
        self.db = None

    async def connect(self):
        self.db = await aiosqlite.connect(self.db_path)

    async def init_db(self):
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                count INTEGER DEFAULT 0,
                max_value INTEGER DEFAULT 100,
                language TEXT DEFAULT 'ru'
            )
        """)

        try:
            await self.db.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru'")
            await self.db.commit()
        except Exception:
            pass

    async def ensure_user(self, user_id: int):
        await self.db.execute(
            "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
            (user_id,)
        )
        await self.db.commit()

    async def increment_count(self, user_id: int):
        await self.db.execute(
            "UPDATE users SET count = count + 1 WHERE user_id = ?",
            (user_id,)
        )
        await self.db.commit()

    async def set_language(self, user_id: int, language: str):
        await self.db.execute(
            "UPDATE users SET language = ? WHERE user_id = ?",
            (language, user_id)
        )
        await self.db.commit()
    
    async def get_language(self, user_id: int) -> str:
        async with self.db.execute(
            "SELECT language FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row and row[0]:
                return row
            return row[0]

    async def get_users_stats(self, user_id: int) -> tuple[int, int]:
        async with self.db.execute(
            "SELECT count, max_value FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return row[0], row[1]
            else:
                return 0, 100

    async def close(self):
        if self.db:
            await self.db.close()