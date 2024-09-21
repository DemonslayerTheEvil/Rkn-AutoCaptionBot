# (c) @RknDeveloperr
# Rkn Developer 
# Don't Remove Credit 😔
# Telegram Channel @RknDeveloper & @Rkn_Botz
# Developer @RknDeveloperr

from pyrogram import Client, filters, errors, types
from config import Rkn_Bots
import asyncio, time, sys
from .database import total_user, getid, delete, addCap, updateCap, insert, chnl_ids
from pyrogram.errors import FloodWait

@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["rknusers"]))
async def all_db_users_here(client, message):
    start_t = time.time()
    rkn = await message.reply_text("Processing...")
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))    
    total_users = await total_user()
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rkn.edit(text=f"**--Bot Processed--** \n\n**Bot Started UpTime:** {uptime} \n**Bot Current Ping:** `{time_taken_s:.3f} ᴍꜱ` \n**All Bot Users:** `{total_users}`")


@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command(["broadcast"]))
async def broadcast(bot, message):
    if message.reply_to_message:
        rkn = await message.reply_text("Bot Processing.\nI am checking all bot users.")
        all_users = await getid()
        tot = await total_user()
        success = failed = deactivated = blocked = 0
        await rkn.edit(f"bot ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ started...")
        async for user in all_users:
            try:
                await message.reply_to_message.copy(user['_id'])
                success += 1
            except errors.InputUserDeactivated:
                deactivated += 1
                await delete({"_id": user['_id']})
            except errors.UserIsBlocked:
                blocked += 1
                await delete({"_id": user['_id']})
            except Exception:
                failed += 1
                await delete({"_id": user['_id']})
                pass
            await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴘʀᴏᴄᴇssɪɴɢ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
        
        await rkn.edit(f"<u>ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</u>\n\n• ᴛᴏᴛᴀʟ ᴜsᴇʀs: {tot}\n• sᴜᴄᴄᴇssғᴜʟ: {success}\n• ʙʟᴏᴄᴋᴇᴅ ᴜsᴇʀs: {blocked}\n• ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs: {deactivated}\n• ᴜɴsᴜᴄᴄᴇssғᴜʟ: {failed}")
        
@Client.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(b, m):
    rkn_msg = await b.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=m.chat.id)       
    await asyncio.sleep(3)
    await rkn_msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)
    
@Client.on_message(filters.command("start") & filters.private)
async def start_cmd(bot, message):
    user_id = int(message.from_user.id)
    await insert(user_id)
    await message.reply_photo(photo=Rkn_Bots.RKN_PIC,
        caption=f"<b>Hey, {message.from_user.mention}\n\nI'm an auto-caption bot. I automatically edit captions for videos, audio files, and documents posted on channels.\n\nUse <code>/set_caption</code> to set a caption\nUse <code>/delcaption</code> to delete caption and set caption to default.\n\nNote: All commands work on channels only</b>",
        reply_markup=types.InlineKeyboardMarkup([[
            types.InlineKeyboardButton('Main Channel', url='https://t.me/lux_botz'),
            types.InlineKeyboardButton('Help Group', url='https://t.me/lux_botz')
        ]]))
    

@Client.on_message(filters.command("set_prefix") & filters.channel)
async def set_prefix(bot, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /set_prefix <your prefix text>")
    chnl_id = message.chat.id
    prefix = message.text.split(" ", 1)[1]
    
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    if chkData:
        await chnl_ids.update_one({"chnl_id": chnl_id}, {"$set": {"prefix": prefix}})
    else:
        await addCap(chnl_id, prefix=prefix)
    await message.reply(f"Prefix set successfully: `{prefix}`")

@Client.on_message(filters.command("set_suffix") & filters.channel)
async def set_suffix(bot, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /set_suffix <your suffix text>")
    chnl_id = message.chat.id
    suffix = message.text.split(" ", 1)[1]
    
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    if chkData:
        await chnl_ids.update_one({"chnl_id": chnl_id}, {"$set": {"suffix": suffix}})
    else:
        await addCap(chnl_id, suffix=suffix)
    await message.reply(f"Suffix set successfully: `{suffix}`")

@Client.on_message(filters.command("delete_prefix") & filters.channel)
async def delete_prefix(bot, message):
    chnl_id = message.chat.id
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    
    if chkData and "prefix" in chkData:
        await chnl_ids.update_one({"chnl_id": chnl_id}, {"$unset": {"prefix": ""}})
        return await message.reply("Prefix has been successfully deleted.")
    else:
        return await message.reply("No prefix found for this channel.")

@Client.on_message(filters.command("delete_suffix") & filters.channel)
async def delete_suffix(bot, message):
    chnl_id = message.chat.id
    chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
    
    if chkData and "suffix" in chkData:
        await chnl_ids.update_one({"chnl_id": chnl_id}, {"$unset": {"suffix": ""}})
        return await message.reply("Suffix has been successfully deleted.")
    else:
        return await message.reply("No suffix found for this channel.")

@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
    if message.media:
        chkData = await chnl_ids.find_one({"chnl_id": chnl_id})
        if chkData:
            prefix = chkData.get("prefix", "")
            suffix = chkData.get("suffix", "")
            caption = message.caption or ""
            new_caption = f"{prefix} {caption} {suffix}".strip()
            await message.edit_caption(new_caption)
