from Barath import mongodb
import asyncio

collection = mongodb["pmpermit"]

PMPERMIT_MESSAGE = (
    "Ok! Stop Right there Read this first before sending any new messages.\n\n"
    "I'm a bot Protecting this user's PM from any kind of Spam."
    "Please wait for my Master to come back Online.\n\n"
    "Until then, Don't spam, Or you'll get blocked and reported!"
)

BLOCKED = "Guess You're A Spammer, Blocked Successfully"

LIMIT = 5


async def set_pm(value: bool):
    doc = {"_id": 1, "pmpermit": value}
    doc2 = {"_id": "Approved", "users": []}
    r = collection.find_one({"_id": 1})
    r2 = collection.find_one({"_id": "Approved"})
    if r:
        await collection.update_one({"_id": 1}, {"$set": {"pmpermit": value}})
    else:
        await collection.insert_one(doc)
    if not r2:
        await collection.insert_one(doc2)


async def set_permit_message(text):
    collection.update_one({"_id": 1}, {"$set": {"pmpermit_message": text}})


async def set_block_message(text):
    collection.update_one({"_id": 1}, {"$set": {"block_message": text}})


async def set_limit(limit):
    collection.update_one({"_id": 1}, {"$set": {"limit": limit}})


async def get_pm_settings():
    result = collection.find_one({"_id": 1})
    if not result:
        return False
    pmpermit = result["pmpermit"]
    pm_message = result.get("pmpermit_message", PMPERMIT_MESSAGE)
    block_message = result.get("block_message", BLOCKED)
    limit = result.get("limit", LIMIT)
    return pmpermit, pm_message, limit, block_message


async def allow_user(chat):
    doc = {"_id": "Approved", "users": [chat]}
    r = collection.find_one({"_id": "Approved"})
    if r:
        await collection.update_one({"_id": "Approved"}, {"$push": {"users": chat}})
    else:
        await collection.insert_one(doc)


async def get_approved_users():
    results = collection.find_one({"_id": "Approved"})
    if results:
        return results["users"]
    else:
        return []


async def deny_user(chat):
    collection.update_one({"_id": "Approved"}, {"$pull": {"users": chat}})


async def pm_guard():
    result = collection.find_one({"_id": 1})
    if not result:
        return False
    if not result["pmpermit"]:
        return False
    else:
        return True
