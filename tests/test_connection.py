# tests/test_connection.py
from jiajia.db.connection import engine


async def test_db_connection():
    async with engine.connect() as conn:
        result = await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        assert result.scalar() == 1
