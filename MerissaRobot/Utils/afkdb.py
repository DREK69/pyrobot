from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from MerissaRobot import MONGO_DB_URI

mongo = MongoClient(MONGO_DB_URI)
db = mongo.AFK

usersdb = db.users


async def is_afk(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    if not user:
        return False, {}
    return True, user["reason"]


async def add_afk(user_id: int, mode):
    await usersdb.update_one(
        {"user_id": user_id}, {"$set": {"reason": mode}}, upsert=True
    )


async def remove_afk(user_id: int):
    user = await usersdb.find_one({"user_id": user_id})
    if user:
        return await usersdb.delete_one({"user_id": user_id})
