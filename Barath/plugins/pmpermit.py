import asyncio
import config
from pyrogram import filters
from pyrogram.methods import messages
from Barath import barath 
from Barath.help.help_func import get_arg, denied_users
import Barath.database.pmpermit as Zectdb


FLOOD_CTRL = 0
ALLOWED = []
USERS_AND_WARNS = {}


@barath.on_message(filters.command("pmguard", prefixes=config.HANDLER) & filters.user(config.OWNER_ID))
async def pmguard(client, message):
    arg = get_arg(message)
    if not arg:
        await message.edit("**I only understand on or off**")
        return
    if arg == "off":
        Zectdb.set_pm(False)
        await message.edit("**PM Guard Deactivated**")
    if arg == "on":
        Zectdb.set_pm(True)
        await message.edit("**PM Guard Activated**")


@barath.on_message(filters.command("setlimit", prefixes=config.HANDLER) & filters.user(config.OWNER_ID))
async def pmguard(client, message):
    arg = get_arg(message)
    if not arg:
        await message.edit("**Set limit to what?**")
        return
    await Zectdb.set_limit(int(arg))
    await message.edit(f"**Limit set to {arg}**")


@barath.on_message(filters.command("setpmmsg", prefixes=config.HANDLER) & filters.user(config.OWNER_ID))
async def setpmmsg(client, message):
    arg = get_arg(message)
    if not arg:
        await message.edit("**What message to set**")
        return
    if arg == "default":
        await Zectdb.set_permit_message(Zectdb.PMPERMIT_MESSAGE)
        await message.edit("**Anti_PM message set to default**.")
        return
    await Zectdb.set_permit_message(f"`{arg}`")
    await message.edit("**Custom anti-pm message set**")


@barath.on_message(filters.command("setblockmsg", prefixes=config.HANDLER) & filters.user(config.OWNER_ID))
async def setpmmsg(client, message):
    arg = get_arg(message)
    if not arg:
        await message.edit("**What message to set**")
        return
    if arg == "default":
        await Zectdb.set_block_message(Zectdb.BLOCKED)
        await message.edit("**Block message set to default**.")
        return
    await Zectdb.set_block_message(f"`{arg}`")
    await message.edit("**Custom block message set**")


@barath.on_message(filters.command("allow", prefixes=config.HANDLER) & filters.user(config.OWNER_ID))
async def allow(client, message):
    chat_id = message.chat.id
    pmpermit, pm_message, limit, block_message = await Zectdb.get_pm_settings()
    Zectdb.allow_user(chat_id)
    await message.edit(f"**I have allowed [you](tg://user?id={chat_id}) to PM me.**")
    async for message in barath.search_messages(
        chat_id=message.chat.id, query=pm_message, limit=1, from_user="me"
    ):
        await message.delete()
    USERS_AND_WARNS.update({chat_id: 0})


@barath.on_message(filters.command("deny", prefixes=config.HANDLER) & filters.user(config.OWNER_ID))
async def deny(client, message):
    chat_id = message.chat.id
    Zectdb.deny_user(chat_id)
    await message.edit(f"**I have denied [you](tg://user?id={chat_id}) to PM me.**")


@barath.on_message(
    filters.private
    & filters.create(denied_users)
    & filters.incoming
    & ~filters.service
    & ~filters.me
    & ~filters.bot
)


async def reply_pm(client, message):
    global FLOOD_CTRL
    pmpermit, pm_message, limit, block_message = await Zectdb.get_pm_settings()
    user = message.from_user.id
    user_warns = 0 if user not in USERS_AND_WARNS else USERS_AND_WARNS[user]
    if user_warns <= limit - 2:
        user_warns += 1
        USERS_AND_WARNS.update({user: user_warns})
        if not FLOOD_CTRL > 0:
            FLOOD_CTRL += 1
        else:
            FLOOD_CTRL = 0
            return
        async for message in barath.search_messages(
            chat_id=message.chat.id, query=pm_message, limit=1, from_user="me"
        ):
            await message.delete()
        await message.reply(pm_message, disable_web_page_preview=True)
        return
    await message.reply(block_message, disable_web_page_preview=True)
    await barath.block_user(message.chat.id)
    USERS_AND_WARNS.update({user: 0})
