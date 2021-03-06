import os

from pyrogram import filters
from pyrogram.types import Message

from wbb import SUDOERS, app
from wbb.core.decorators.errors import capture_err
from wbb.utils.dbfunctions import is_gbanned_user, user_global_karma

__MODULE__ = "Info"
__HELP__ = """
/info [USERNAME|ID] - Get info about a user.
/chat_info [USERNAME|ID] - Get info about a chat.
"""


async def get_user_info(user):
    user = await app.get_users(user)
    if not user.first_name:
        return ["Deleted account", None]
    user_id = user.id
    username = user.username
    first_name = user.first_name
    mention = user.mention("Link")
    status = user.status
    dc_id = user.dc_id
    photo_id = user.photo.big_file_id if user.photo else None
    is_gbanned = await is_gbanned_user(user_id)
    is_sudo = user_id in SUDOERS
    karma = await user_global_karma(user_id)
    caption = f"""
**ID:** `{user_id}`
**DC:** {dc_id}
**Name:** {first_name}
**Username:** {("@" + username) if username else None}
**Permalink:** {mention}
**Status:** {status}
**Sudo:** {is_sudo}
**Karma:** {karma}
**Gbanned:** {is_gbanned}
"""
    return [caption, photo_id]


async def get_chat_info(chat):
    chat = await app.get_chat(chat)
    chat_id = chat.id
    username = chat.username
    title = chat.title
    type = chat.type
    is_scam = chat.is_scam
    description = chat.description
    members = chat.members_count
    is_restricted = chat.is_restricted
    link = f"[Link](t.me/{username})" if username else None
    dc_id = chat.dc_id
    photo_id = chat.photo.big_file_id if chat.photo else None
    caption = f"""
**ID:** `{chat_id}`
**DC:** {dc_id}
**Type:** {type}
**Name:** {title}
**Username:** {("@" + username) if username else None}
**Permalink:** {link}
**Members:** {members}
**Scam:** {is_scam}
**Restricted:** {is_restricted}
**Description:** {description}
"""
    return [caption, photo_id]


@app.on_message(filters.command("info"))
@capture_err
async def info_func(_, message: Message):
    try:
        if message.reply_to_message:
            user = message.reply_to_message.from_user.id
        elif not message.reply_to_message and len(message.command) == 1:
            user = message.from_user.id
        elif not message.reply_to_message and len(message.command) != 1:
            user = message.text.split(None, 1)[1]
        m = await message.reply_text("Processing")
        info_caption, photo_id = await get_user_info(user)
        if not photo_id:
            return await m.edit(info_caption, disable_web_page_preview=True)
        photo = await app.download_media(photo_id)
        await message.reply_photo(photo, caption=info_caption, quote=False)
        await m.delete()
        os.remove(photo)
    except Exception as e:
        await message.reply_text(str(e))
        print(e)


@app.on_message(filters.command("chat_info"))
@capture_err
async def chat_info_func(_, message: Message):
    try:
        if len(message.command) > 2:
            return await message.reply_text(
                "**Usage:**/chat_info [USERNAME|ID]"
            )
        elif len(message.command) == 1:
            chat = message.chat.id
        elif len(message.command) == 2:
            chat = message.text.split(None, 1)[1]
        m = await message.reply_text("Processing")
        info_caption, photo_id = await get_chat_info(chat)
        if not photo_id:
            return await m.edit(info_caption, disable_web_page_preview=True)
        photo = await app.download_media(photo_id)
        await message.reply_photo(photo, caption=info_caption, quote=False)
        await m.delete()
        os.remove(photo)
    except Exception as e:
        await message.reply_text(e)
        print(e)
