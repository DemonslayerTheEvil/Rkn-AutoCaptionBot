from pyrogram import Client, filters, errors, types
from config import Rkn_Bots
import asyncio, re, time, sys, os
from .database import total_user, getid, delete, addCap, updateCap, insert, chnl_ids
from pyrogram.errors import FloodWait

# Command to view bot users
@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["rknusers"]))
async def all_db_users_here(client, message):
    start_t = time.time()
    rkn = await message.reply_text("Processing...")
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))    
    total_users = await total_user()
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rkn.edit(text=f"**--Bot Processed--** \n\n**Bot Started UpTime:** {uptime} \n**Bot Current Ping:** `{time_taken_s:.3f} ms` \n**All Bot Users:** `{total_users}`")

# Command for broadcasting messages to users
@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    if message.reply_to_message:
        rkn = await message.reply_text("Bot Processing. Checking all bot users.")
        all_users = await getid()
        tot = await total_user()
        success, failed, deactivated, blocked = 0, 0, 0, 0
        await rkn.edit(f"Broadcasting started...")
        
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
            
            try:
                await rkn.edit(f"<u>Broadcast Progress</u>\n\n• Total Users: {tot}\n• Successful: {success}\n• Blocked Users: {blocked}\n• Deactivated Accounts: {deactivated}\n• Unsuccessful: {failed}")
            except FloodWait as e:
                await asyncio.sleep(e.x)

        await rkn.edit(f"<u>Broadcast Completed</u>\n\n• Total Users: {tot}\n• Successful: {success}\n• Blocked Users: {blocked}\n• Deactivated Accounts: {deactivated}\n• Unsuccessful: {failed}")

# Command to restart the bot
@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(b, m):
    rkn_msg = await b.send_message(text="🔄 Processes stopped. Restarting bot...", chat_id=m.chat.id)       
    await asyncio.sleep(3)
    await rkn_msg.edit("✅ Bot restarted. You can now use it.")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Command to start the bot
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    user_id = int(message.from_user.id)
    await insert(user_id)
    await message.reply_photo(
        photo=Rkn_Bots.RKN_PIC,
        caption=f"<b>Hey, {message.from_user.mention}\n\nI'm an auto-caption bot. I automatically edit captions for videos, audio files, and documents posted on channels.\n\nUse <code>/set_caption</code> to set caption\nUse <code>/delcaption</code> to delete caption and set it to default.\n\nNote: All commands work on channels only.</b>",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton('Main Channel', url='https://t.me/RknDeveloper'),
            types.InlineKeyboardButton('Help Group', url='https://t.me/Rkn_Bots_Support')
            ],[
            types.InlineKeyboardButton('🔥 Source Code 🔥', url='https://github.com/RknDeveloper/Rkn-AutoCaptionBot')
    ]]))

# Command to set a custom caption
@Client.on_message(filters.command(["set_caption", "set"]) & filters.channel)
async def set_caption(bot, message):
    if len(message.command) < 2:
        return await message.reply(
            "<b>Provide a caption to set</b>\n<u>Example:</u> ⬇️\n\n<code>/set_caption {file_name}\n\n{file_caption}\n\nsize » {file_size}\n\nJoin :- @your_channel</code>"
        )
    chnl_id = message.chat.id
    caption = message.text.split(" ", 1)[1]
    chk_data = await chnl_ids.find_one({"chnl_id": chnl_id})
    if chk_data:
        await updateCap(chnl_id, caption)
        return await message.reply(f"Caption updated successfully:\n\n`{caption}`")
    else:
        await addCap(chnl_id, caption)
        return await message.reply(f"Caption added successfully:\n\n`{caption}`")

# Command to delete a custom caption
@Client.on_message(filters.command(["delcaption", "del_caption", "delete_caption"]) & filters.channel)
async def del_caption(_, msg):
    chnl_id = msg.chat.id
    try:
        await chnl_ids.delete_one({"chnl_id": chnl_id})
        return await msg.reply("<b>Caption deleted successfully. Default caption will be used.</b>")
    except Exception as e:
        rkn = await msg.reply(f"Error: {e}")
        await asyncio.sleep(5)
        await rkn.delete()

# Command to view the current caption
@Client.on_message(filters.command("view") & filters.channel)
async def view_caption(bot, message):
    chnl_id = message.chat.id
    chk_data = await chnl_ids.find_one({"chnl_id": chnl_id})
    if chk_data:
        current_caption = chk_data["caption"]
        return await message.reply(f"Your Current Caption:\n`{current_caption}`")
    else:
        return await message.reply("<b>No custom caption set. Using the default caption.</b>")

# Automatically edit captions for files
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

                file_name = re.sub(r"@\w+\s*", "", file_name).replace("_", " ").replace(".", " ")

                cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})
                try:
                    if cap_dets:
                        cap = cap_dets["caption"]
                        replaced_caption = cap.format(
                            file_name=file_name,
                            file_size=file_size_text,
                            file_caption=message.caption or "No caption"
                        )
                        await message.edit(replaced_caption)
                    else:
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
