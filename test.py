import asyncio
from data.db_games_functions import get_all_users

if __name__ == "__main__":
    asyncio.run(get_all_users())