import os
import time
import requests
from flask import Flask

# Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
FORCE_SUB_CHANNEL = "Allutvserials"

# Simple Flask server for Render keep-alive
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running perfectly!"

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

def check_subscription(user_id):
    if user_id == ADMIN_ID:
        return True
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id=@{FORCE_SUB_CHANNEL}&user_id={user_id}"
    try:
        response = requests.get(url).json()
        status = response.get("result", {}).get("status")
        if status in ["member", "administrator", "creator"]:
            return True
    except Exception:
        pass
    return False

# 22 Inline Buttons Menu
def get_video_menu():
    return {
        "inline_keyboard": [
            [{"text": "🖼️ Thumb Extractor", "callback_data": "thumb_extract"},
             {"text": "✏️ Caption Editor", "callback_data": "caption_edit"}],
            [{"text": "📋 Metadata Editor", "callback_data": "meta_edit"},
             {"text": "🔀 Stream Mapper", "callback_data": "stream_map"}],
            [{"text": "❌ Stream Remover", "callback_data": "stream_remove"},
             {"text": "📥 Stream Extractor", "callback_data": "stream_extract"}],
            [{"text": "✂️ Video Trimmer", "callback_data": "video_trim"},
             {"text": "➕ Video Merger", "callback_data": "video_merge"}],
            [{"text": "🔇 Remove Audio", "callback_data": "remove_audio"},
             {"text": "🔀 Merge Audio & Video", "callback_data": "merge_AV"}],
            [{"text": "🎵 Audio Converter", "callback_data": "audio_conv"},
             {"text": "✂️ Videos Splitter", "callback_data": "video_split"}],
            [{"text": "🖼️ Screenshots", "callback_data": "screenshots"},
             {"text": "📸 Manual Shots", "callback_data": "manual_shots"}],
            [{"text": "📊 Generate Sample", "callback_data": "gen_sample"},
             {"text": "🔊 Video To Audio", "callback_data": "vid_to_audio"}],
            [{"text": "⚡ Video Optimizer", "callback_data": "vid_optimize"},
             {"text": "💬 Subtitle Merger", "callback_data": "sub_merge"}],
            [{"text": "🔄 Video Converter", "callback_data": "vid_conv"},
             {"text": "✏️ Video Renamer", "callback_data": "vid_rename"}],
            [{"text": "ℹ️ Media Information", "callback_data": "media_info"},
             {"text": "📦 Create Archive", "callback_data": "create_archive"}]
        ]
    }

user_tasks = {}
MAX_USER_TASKS = 2

def main():
    offset = 0
    print("Pure Python Telegram Bot Started Successfully!")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url).json()
            
            if response.get("ok"):
                for update in response.get("result", []):
                    offset = update["update_id"] + 1
                    
                    # Handle Messages
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        user_id = msg["from"]["id"]
                        text = msg.get("text", "")
                        
                        # Check Force Subscription
                        if not check_subscription(user_id):
                            # നിങ്ങളുടെ ബോട്ടിന്റെ യൂസർനെയിം താഴെ കൊടുക്കുക (ഉദാഹരണത്തിന്: t.me/YourBotUsername)
                            bot_username = "AlluVideoBot" # ഇവിടെ നിങ്ങളുടെ ബോട്ടിന്റെ യൂസർനെയിം നൽകുക
                            keyboard = {
                                "inline_keyboard": [
                                    [{"text": "📢 Join Channel", "url": f"https://t.me/{FORCE_SUB_CHANNEL}"}],
                                    [{"text": "🔄 Try Again", "url": f"https://t.me/{bot_username}?start=start"}]
                                ]
                            }
                            send_message(chat_id, f"⚠️ **Access Denied!**\nPlease join our update channel @{FORCE_SUB_CHANNEL} to use this bot.", reply_markup=keyboard)
                            continue
                        
                        # /start Command
                        if text.startswith("/start"):
                            welcome_text = (
                                "👋 **Welcome to the Advanced Video Editing Bot!**\n\n"
                                "I am your all-in-one assistant for managing, trimming, converting, and editing videos seamlessly. "
                                "Send any video or document to get started!"
                            )
                            keyboard = {
                                "inline_keyboard": [
                                    [{"text": "📞 Contact Admin", "url": "https://t.me/anujith1238"}]
                                ]
                            }
                            send_message(chat_id, welcome_text, reply_markup=keyboard)
                        
                        # /settings Command
                        elif text.startswith("/settings"):
                            settings_text = "⚙️ **Bot Settings Menu**\n\nConfigure your preferences below:"
                            send_message(chat_id, settings_text, reply_markup=get_video_menu())
                        
                        # Handle Videos or Documents
                        elif "video" in msg or "document" in msg:
                            if user_id != ADMIN_ID:
                                current_tasks = user_tasks.get(user_id, 0)
                                if current_tasks >= MAX_USER_TASKS:
                                    send_message(chat_id, "⚠️ You can only use 2 tasks at a time. Please wait for your current tasks to finish.")
                                    continue
                                user_tasks[user_id] = current_tasks + 1
                            
                            send_message(chat_id, "🎬 **Video received successfully!** Please choose your required option from below:", reply_markup=get_video_menu())
                    
                    # Handle Callback Queries (Button clicks)
                    elif "callback_query" in update:
                        cq = update["callback_query"]
                        cq_id = cq["id"]
                        chat_id = cq["message"]["chat"]["id"]
                        data = cq["data"]
                        
                        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={"callback_query_id": cq_id, "text": f"Selected: {data}"})
                        send_message(chat_id, f"✅ You selected option: **{data}**")
                            
        except Exception as e:
            print(f"Polling Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))).start()
    main()
