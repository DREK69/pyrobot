from MerissaRobot.Database.mongo import db

impdb = db["imposter"]


async def usr_data(user_id: int) -> bool:
    user = impdb.find_one({"user_id": user_id})
    return bool(user)


async def get_userdata(user_id: int) -> bool:
    user = impdb.find_one({"user_id": user_id})
    return user["username"], user["first_name"], user["last_name"]


async def add_userdata(user_id: int, username, first_name, last_name):
    impdb.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        },
        upsert=True,
    )


async def check_imposter(chat_id: int) -> bool:
    chat = impdb.find_one({"chat_id_toggle": chat_id})
    return bool(chat)


async def impo_on(chat_id: int) -> bool:
    impdb.insert_one({"chat_id_toggle": chat_id})


async def impo_off(chat_id: int):
    impdb.delete_one({"chat_id_toggle": chat_id})
