import aiosqlite
import os


DB_PATH = "data/databases/games.db"

async def get_all_users():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users_words") as cursor:
            rows = await cursor.fetchall()
            for row in rows:
                print(row)

#bu malumotlar bazasi foydalanuvhi yaratgan file malumotlarini saqlaydi
#bu funksiya ma'lumotlar bazasi avval yaratilmagan bo'lsa uni yaratadi.
async def init_db():
    
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users_words(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                words_file_name TEXT NOT NULL,
                words_file_creator_name TEXT NOT NULL,
                words_file_path TEXT NOT NULL,
                words_number INTEGER NOT NULL
            )            
        """)
        await db.commit()



#Ma'lumotlar bazasiga ma'lumotni saqlash uchun foydalaniadi
#Used to store data in a database
async def save_dates(user_id, words_file_name, words_file_creator_name, words_file_path, words_number):
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("""
                INSERT INTO users_words (user_id, words_file_name, words_file_creator_name, words_file_path, words_number)    
                VALUES (?, ?, ?, ?, ?)""",
                (user_id, words_file_name, words_file_creator_name, words_file_path, words_number)
            ) as cur:
                await db.commit()
                return cur.lastrowid
    except Exception as e:
        print(f"ERROR,  {e}")
        
        
#bu funksiya malumotlar bazasidan foydalanuvhininig user_id si orqali foydalanuvshi yaratgan faylninig id va nomini list shaklida qaytaradi 
async def get_dates_id(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT id , words_file_name FROM users_words WHERE user_id=?""",
            (user_id,)
        ) as cur:
            rows = await cur.fetchall()
            return rows if rows else None
    

# bu funksiya foydalanuvchi id raqami orqali oldin bunday nomli fayl yaratgan yoki yo'qligini tekshiradi
async def get_file_name(user_id , file_name):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT words_file_name FROM users_words WHERE user_id=?""",
            (user_id,)
        ) as cur:
            rows = await cur.fetchall()
            for name in rows:
                if file_name == name[0]:
                    return False
            return True
            
    
# bu funksiya foydalanuvchi yaratgan malumotlari id raqami orqali bu ma'lumotlarni barchasini qaytaradi
async def get_dates_all(id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT user_id, words_file_name, words_file_creator_name, words_number FROM users_words WHERE id=?""",
            (id,)
        ) as cur:
            row = await cur.fetchone()
            return row if row else None



# bu funksiya file id raqami orqali uninig manzilini qaytaradi
async def get_file_path(game_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT words_file_path FROM users_words WHERE id=?",
                              (game_id,)
        ) as cur:
            row = await cur.fetchone()
            return row[0]
            

        

# bu funksiya file id raqami orqali uninig malumotlarini o'chiradi
async def delete_game_data(game_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM users_words WHERE id=?",
                         (game_id,)
        )
        await db.commit()        
        


# bu funksiya o'yinga yangi so'zlar qo'shilganda so'zlar sonini yangilaydi
async def update_words_number(game_id, added_words):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users_words SET words_number = words_number + ? WHERE id = ?",
            (added_words, game_id)
        )
        await db.commit()
