from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from config import Rkn_Bots
from .database import chnl_ids
import asyncio
import re
from caption_format import add_prefix_suffix

@Client.on_message(filters.channel)
async def auto_edit_caption(bot, message):
    chnl_id = message.chat.id
    if message.media:
        for file_type in ("video", "audio", "document", "voice"):
            obj = getattr(message, file_type, None)
            if obj and hasattr(obj, "file_name"):
                file_name = obj.file_name
                # Clean the file name (remove username, replace _ and .)
                file_name = re.sub(r"@\w+\s*", "", file_name).replace("_", " ").replace(".", " ")

                cap_dets = await chnl_ids.find_one({"chnl_id": chnl_id})
                try:
                    if cap_dets:
                        # Retrieve the custom caption from the database
                        cap = cap_dets.get("caption", "")
                        
                        # Add the prefix and suffix using the provided function
                        formatted_caption = add_prefix_suffix(file_name, prefix="📂", suffix="#File")
                        
                        # Replace placeholders in the caption with the formatted file name
                        replaced_caption = cap.format(file_name=formatted_caption)
                        
                        # Edit the message caption
                        await message.edit_caption(replaced_caption)
                    else:
                        # If no custom caption is found, use a default caption
                        formatted_caption = add_prefix_suffix(file_name, prefix="📂", suffix="#File")
                        default_caption = Rkn_Bots.DEF_CAP.format(file_name=formatted_caption)
                        await message.edit_caption(default_caption)
                except FloodWait as e:
                    # Handle flood wait errors
                    await asyncio.sleep(e.x)
                    continue
    return
