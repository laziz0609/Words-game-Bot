import aiosqlite
import os



DB_PATH = "data/databases/users.db"


# bu funksiya foydalanuvchilar malumotlar bazasini yaratadi (agarda bo'lmasa)
async def init_db():
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                user_name TEXT
            )               
        """)
        await db.commit()


# bu funksiya foydalanuvchi id va ismini malumotlar bazasiga saqlaydi
async def save_user(user_id , user_name):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users(user_id , user_name)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                user_name = excluded.user_name                 
            """,
            (user_id , user_name)
        )
        await db.commit()
        
        
#bu funksiya foydalanuvchininig ismini malumotlar bazasidan olib chiqadi
async def get_user(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT user_name FROM users WHERE user_id=?
        """,
        (user_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0] if row else None