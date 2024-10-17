from pyrogram import Client, filters, errors, types
from config import Rkn_Bots
import asyncio, re, time, sys, os
from .database import total_user, getid, delete, addCap, updateCap, insert, chnl_ids
from pyrogram.errors import FloodWait

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["users"]))
async def all_db_users_here(client, message):
    start_t = time.time()
    rkn = await message.reply_text("Processing...")
    total_users = await total_user()
    user_list = await getid()
    
    user_info = "\n".join(
        [f"ðŸ‘¤ Name: <a href='tg://user?id={user['_id']}'>{user['first_name']}</a>\nðŸ•µðŸ»â€â™‚ï¸ Username: @{user['username']}\n" for user in user_list]
    )

    await rkn.edit(
        f"**--Bot Users--** \n\n**Total Users:** `{total_users}`\n\n{user_info}"
    )


@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    if message.reply_to_message:
        rkn = await message.reply_text("Bot Processing.\nI am checking all bot users.")
        all_users = await getid()
        tot = await total_user()
        success = 0
        failed = 0
        deactivated = 0
        blocked = 0
        await rkn.edit(f"bot broadcasting started...")
        async for user in all_users:
            try:
                time.sleep(1)
                await message.reply_to_message.copy(user['_id'])
                success += 1
            except errors.InputUserDeactivated:
                deactivated += 1
                await delete({"_id": user['_id']})
            except errors.UserIsBlocked:
                blocked += 1
                await delete({"_id": user['_id']})
            except Exception as e:
                failed += 1
                await delete({"_id": user['_id']})
                pass
            try:
                await rkn.edit(f"<u>Broadcast Processing</u>\n\nâ€¢ Total users: {tot}\nâ€¢ Successful: {success}\nâ€¢ Blocked users: {blocked}\nâ€¢ Deleted accounts: {deactivated}\nâ€¢ Unsuccessful: {failed}")
            except FloodWait as e:
                await asyncio.sleep(e.x)
        await rkn.edit(f"<u>Broadcast Completed</u>\n\nâ€¢ Total users: {tot}\nâ€¢ Successful: {success}\nâ€¢ Blocked users: {blocked}\nâ€¢ Deleted accounts: {deactivated}\nâ€¢ Unsuccessful: {failed}")


@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(b, m):
    rkn_msg = await b.send_message(text="**ðŸ”„ Processes stopped. Bot is restarting...**", chat_id=m.chat.id)
    await asyncio.sleep(3)
    await rkn_msg.edit("**âœ… Bot is restarted. You can now use me**")
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    user_id = int(message.from_user.id)
    await insert(user_id)
    await message.reply_photo(photo=Rkn_Bots.RKN_PIC,
        caption=f"<b>Hey, {message.from_user.mention}\n\nI'm an auto-caption bot. I automatically edit captions for videos, audio files, and documents posted on channels.\n\nUse <code>/set_caption</code> to set caption\nUse <code>/delcaption</code> To delete caption and set caption to default.\n\nNote: All commands work on channels only</b>",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton('Main Channel', url='https://t.me/RxBotz'),
            types.InlineKeyboardButton('Help Group', url='https://t.me/RxBotz')
            ],[
            types.InlineKeyboardButton('ðŸ”¥ Source Code ðŸ”¥', url='https://t.me/code_lelo/2')
        ]]))


@Client.on_message(filters.command(["set_caption", "set"]) & filters.channel)
async def setCaption(bot, message):
    if len(message.command) < 2:
        return await message.reply(
            "<b>give me a caption to set</b>\n<u>Example:- â¬‡ï¸</u>\n\n<code>/set_caption {file_name}\n\n{file_caption}\n\nsize Â» {file_size}\n\nJoin :- @your_channel</code>"
        )
    chnl_id = message.chat.id
    caption = (
        message.text.split(" ", 1)[1] if len(message.text.split(" ", 1)) > 1 else None
    )
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    if chkData:
        await updateCap(chnl_id, caption)
        return await message.reply(f"Successfully Updated Your Caption.\n\nYour New Caption: `{caption}`")
    else:
        await addCap(chnl_id, caption)
        return await message.reply(f"Successfully Updated Your Caption.\n\nYour New Caption: `{caption}`")


@Client.on_message(filters.command(["delcaption", "del_caption", "delete_caption"]) & filters.channel)
async def delCaption(_, msg):
    chnl_id = msg.chat.id
    try:
        await chnl_ids.delete_one({"chnl_id": chnl_id})
        return await msg.reply("<b>Successfully deleted your caption. From now, I will use my default caption</b>")
    except Exception as e:
        rkn = await msg.reply(f"Error: {e}")
        await asyncio.sleep(5)
        await rkn.delete()
        return


@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
    if message.media:
        for file_type in ("video", "audio", "document", "voice"):
            obj = getattr(message, file_type, None)
            if obj and hasattr(obj, "file_name"):
                file_name = obj.file_name
                file_size = obj.file_size  # Get file size in bytes

                # Convert file size to human-readable format
                if file_size < 1024:
                    file_size_text = f"{file_size} B"
                elif file_size < 1024**2:
                    file_size_text = f"{file_size / 1024:.2f} KB"
                elif file_size < 1024**3:
                    file_size_text = f"{file_size / 1024**2:.2f} MB"
                else:
                    file_size_text = f"{file_size / 1024**3:.2f} GB"

                file_name = (
                    re.sub(r"@\w+\s*", "", file_name)
                    .replace("_", " ")
                    .replace(".", " ")
                )

                cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})
                try:
                    if cap_dets:
                        cap = cap_dets["caption"]

                        # Format the caption using file_name, file_size, and file_caption (original caption)
                        replaced_caption = cap.format(
                            file_name=file_name,
                            file_size=file_size_text,
                            file_caption=message.caption or "No caption"
                        )

                        await message.edit(replaced_caption)
                    else:
                        # If no custom caption is set, use the default caption
                        replaced_caption = Rkn_Bots.DEF_CAP.format(
                            file_name=file_name,
                            file_size=file_size_text,
                            file_caption=message.caption or "No caption"
                        )
                        await message.edit(replaced_caption)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    continue
    return
