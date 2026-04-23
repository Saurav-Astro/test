import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def run():
    client = AsyncIOMotorClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME', 'proxm')]
    cols = await db.list_collection_names()
    print(f'\nTotal tables (collections) present: {len(cols)}\n')
    for c in cols:
        count = await db[c].count_documents({})
        print(f'- {c} (Documents: {count})')

if __name__ == '__main__':
    asyncio.run(run())
