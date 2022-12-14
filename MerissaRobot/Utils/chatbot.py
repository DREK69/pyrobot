from MerissaRobot.Database.mongo import client as db_x

merissa = db_x["MerissaChatBot"]


def add_chat(chat_id):
    stark = merissa.find_one({"chat_id": chat_id})
    if stark:
        return False
    merissa.insert_one({"chat_id": chat_id})
    return True


def remove_chat(chat_id):
    stark = merissa.find_one({"chat_id": chat_id})
    if not stark:
        return False
    merissa.delete_one({"chat_id": chat_id})
    return True


def get_all_chats():
    r = list(merissa.find())
    if r:
        return r
    return False


def get_session(chat_id):
    stark = merissa.find_one({"chat_id": chat_id})
    if not stark:
        return False
    return stark
