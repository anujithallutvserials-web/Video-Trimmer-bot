import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

# Loading configuration safely from Environment Variables
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
FORCE_SUB_CHANNEL = "Allutvserials"

# Initialize the Bot Client
app = Client("video_trimmer_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Track active tasks for users
user_tasks = {}
MAX_USER_TASKS = 2

# 22 Inline Buttons Menu
def get_video_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🖼️ Thumb Extractor", callback_data="thumb_extract"),
         InlineKeyboardButton("✏️ Caption Editor", callback_data="caption_edit")],
        [InlineKeyboardButton("📋 Metadata Editor", callback_data="meta_edit"),
         InlineKeyboardButton("🔀 Stream Mapper", callback_data="stream_map")],
        [InlineKeyboardButton("❌ Stream Remover", callback_data="stream_remove"),
         InlineKeyboardButton("📥 Stream Extractor", callback_data="stream_extract")],
        [InlineKeyboardButton("✂️ Video Trimmer", callback_data="video_trim"),
         InlineKeyboardButton("➕ Video Merger", callback_data="video_merge")],
        [InlineKeyboardButton("🔇 Remove Audio", callback_data="remove_audio"),
         InlineKeyboardButton("🔀 Merge Audio & Video", callback_data="merge_AV")],
        [InlineKeyboardButton("🎵 Audio Converter", callback_data="audio_conv"),
         InlineKeyboardButton("✂️ Videos Splitter", callback_data="video_split")],
        [InlineKeyboardButton("🖼️ Screenshots", callback_data="screenshots"),
         InlineKeyboardButton("📸 Manual Shots", callback_data="manual_shots")],
        [InlineKeyboardButton("📊 Generate Sample", callback_data="gen_sample"),
         InlineKeyboardButton("🔊 Video To Audio", callback_data="vid_to_audio")],
        [InlineKeyboardButton("⚡ Video Optimizer", callback_data="vid_optimize"),
         InlineKeyboardButton("💬 Subtitle Merger", callback_data="sub_merge")],
        [InlineKeyboardButton("🔄 Video Converter", callback_data="vid_conv"),
         InlineKeyboardButton("✏️ Video Renamer", callback_data="vid_rename")],
        [InlineKeyboardButton("ℹ️ Media Information", callback_data="media_info"),
         InlineKeyboardButton("📦 Create Archive", callback_data="create_archive")]
    ])

# Function to check Force Subscription
async def is_subscribed(client, user_id):
    if user_id == ADMIN_ID:
        return True
    try:
        user = await client.get_chat_member(FORCE_SUB_CHANNEL, user_id)
        if user.status in ["banned", "left"]:
            return False
        return True
    except UserNotParticipant:
        return False
    except Exception:
        return True

# /start Command Handler
@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    
    if not await is_subscribed(client, user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")],
            [InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{client.me.username}?start=start")]
        ])
        await message.reply(
            "⚠️ **Access Denied!**\n\n"
            f"You must join our update channel @{FORCE_SUB_CHANNEL} to use this bot.\n"
            "Please join the channel and click 'Try Again'.",
            reply_markup=keyboard
        )
        return

    welcome_text = (
        "👋 **Welcome to the Advanced Video Editing Bot!**\n\n"
        "I am your all-in-one assistant for managing, trimming, converting, and editing videos seamlessly. "
        "Just send any video or document to get started with our powerful features!\n\n"
        "✨ *Features include Trimming, Merging, Audio Extraction, Watermarking, Subtitle tools, and much more!*"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/anujith1238")]
    ])
    
    await message.reply(welcome_text, reply_markup=keyboard)

# Handle incoming videos and documents
@app.on_message(filters.video | filters.document)
async def handle_video(client, message):
    user_id = message.from_user.id
    
    if not await is_subscribed(client, user_id):
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_SUB_CHANNEL}")]
        ])
        await message.reply(
            "⚠️ **Subscription Required!**\n\n"
            f"Please join our channel @{FORCE_SUB_CHANNEL} first to use this bot.",
            reply_markup=keyboard
        )
        return

    if user_id != ADMIN_ID:
        current_tasks = user_tasks.get(user_id, 0)
        
        if current_tasks >= MAX_USER_TASKS:
            await message.reply(
                "⚠️ You can only use 2 tasks at a time. "
                "Please wait for your current tasks to finish before downloading more."
            )
            return
        
        user_tasks[user_id] = current_tasks + 1

    await message.reply(
        "🎬 **Video received successfully!** Please choose your required option from below:",
        reply_markup=get_video_menu()
    )

if __name__ == "__main__":
    print("Starting Telegram Bot...")
    app.run()
