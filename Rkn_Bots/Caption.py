import os
import re
import time
import sys
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from database import total_user, remove_user, getid

class Rkn_Bots:
    ADMIN = [7252430326]  # Replace with your admin ID
    START_TIME = time.time()

app = Client("my_bot")

# Broadcast Command
@app.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("broadcast"))
async def broadcast(client, message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a message to broadcast.")
        return

    broadcast_msg = message.reply_to_message
    sent = 0
    failed = 0

    users = await getid()
    for user_id in users:
        try:
            await client.copy_message(
                chat_id=user_id,
                from_chat_id=broadcast_msg.chat.id,
                message_id=broadcast_msg.message_id
            )
            sent += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
        except Exception as e:
            failed += 1
            await remove_user(user_id)  # Remove user from DB if failed

    await message.reply_text(f"Broadcast completed:\nSent: {sent}\nFailed: {failed}")

# Show total users
@app.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("rknusers"))
async def rknusers(client, message):
    user_count = await total_user()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - Rkn_Bots.START_TIME))
    await message.reply_text(f"Total Users: {user_count}\nUptime: {uptime}")

# Restart bot
@app.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("restart"))
async def restart_bot(client, message):
    await message.reply_text("Restarting bot...")
    os.execl(sys.executable, sys.executable, *sys.argv)

# Bot Status (NEW)
@app.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("status"))
async def bot_status(client, message):
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - Rkn_Bots.START_TIME))
    user_count = await total_user()
    await message.reply_text(f"Bot is running.\nUptime: {uptime}\nTotal Users: {user_count}")

# Delete caption in channels
@app.on_message(filters.channel & filters.user(Rkn_Bots.ADMIN) & filters.command(["delcaption", "del_caption", "delete_caption"]))
async def delete_caption(client, message):
    if message.reply_to_message:
        await message.reply_to_message.edit_caption(caption="")
        await message.reply_text("Caption deleted.")
    else:
        await message.reply_text("Reply to a message to delete its caption.")

# New /remove command for media titles
@app.on_message(filters.private & filters.user(Rkn_Bots.ADMIN) & filters.command("remove"))
async def remove_in_title(client, message):
    if message.reply_to_message and message.reply_to_message.caption:
        old_caption = message.reply_to_message.caption
        unwanted_words = ['USERNAME', 'ExampleWord']  # Add words to remove
        cleaned_caption = re.sub('|'.join(unwanted_words), '', old_caption, flags=re.IGNORECASE).strip()
        await message.reply_to_message.edit_caption(cleaned_caption)
        await message.reply_text("Removed unwanted words from caption.")
    else:
        await message.reply_text("Reply to a message with a caption to remove unwanted words.")

# Start bot
app.run()
