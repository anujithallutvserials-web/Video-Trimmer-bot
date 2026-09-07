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
        response = requests.post(url, json=payload)
        return response.json().get("result", {}).get("message_id")
    except Exception as e:
        print(f"Error sending message: {e}")
    return None

def edit_message_text(chat_id, message_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error editing message: {e}")

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
user_states = {}  # യൂസർ ഇപ്പോൾ ഏത് മോഡിലാണ് എന്ന് അറിയാൻ (ഉദാഹരണത്തിന്: video_merge)
MAX_USER_TASKS = 2

def main():
    offset = 0
    print("Advanced Telegram Bot with State Management Started Successfully!")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url).json()
            
            if response.get("ok"):
                for update in response.get("result", []):
                    offset = update["update_id"] + 1
                    
                    # 1. Handle Messages (Text, Videos, Documents)
                    if "message" in update:
                        msg = update["message"]
                        chat_id = msg["chat"]["id"]
                        user_id = msg["from"]["id"]
                        text = msg.get("text", "")
                        
                        # Force Subscription Check
                        if not check_subscription(user_id):
                            bot_username = "AlluVideoBot"
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
                            user_states[user_id] = None  # സ്റ്റേറ്റ് ക്ലിയർ ചെയ്യുന്നു
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
                            user_states[user_id] = None
                            settings_text = "⚙️ **Bot Settings Menu**\n\nConfigure your preferences below:"
                            send_message(chat_id, settings_text, reply_markup=get_video_menu())
                        
                        # Handle Videos or Documents
                        elif "video" in msg or "document" in msg:
                            current_state = user_states.get(user_id)
                            
                            # യൂസർ ഏതെങ്കിലും പ്രത്യേക ഫീച്ചറിലാണോ ഉള്ളതെന്ന് നോക്കുന്നു (ഉദാ: video_merge)
                            if current_state == "video_merge":
                                send_message(chat_id, "📥 Video received for **Video Merger**. Send more videos or type /done to process.")
                                continue
                            elif current_state == "video_trim":
                                send_message(chat_id, "✂️ Video received for **Video Trimmer**. Send start/end timestamps.")
                                continue
                            elif current_state:
                                send_message(chat_id, f"⚙️ Video received for **{current_state}**. Processing your request...")
                                continue
                            
                            # സാധാരണ രീതിയിൽ വീഡിയോ അയക്കുമ്പോൾ മാത്രം മെനു കാണിക്കുന്നു
                            if user_id != ADMIN_ID:
                                current_tasks = user_tasks.get(user_id, 0)
                                if current_tasks >= MAX_USER_TASKS:
                                    send_message(chat_id, "⚠️ You can only use 2 tasks at a time. Please wait for your current tasks to finish.")
                                    continue
                                user_tasks[user_id] = current_tasks + 1
                            
                            send_message(chat_id, "🎬 **Video received successfully!** Please choose your required option from below:", reply_markup=get_video_menu())
                    
                    # 2. Handle Callback Queries (Button Clicks)
                    elif "callback_query" in update:
                        cq = update["callback_query"]
                        cq_id = cq["id"]
                        chat_id = cq["message"]["chat"]["id"]
                        message_id = cq["message"]["message_id"]
                        user_id = cq["from"]["id"]
                        data = cq["data"]
                        
                        # ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ ആ പഴയ 22 ബട്ടണുകൾ ആ മെസ്സേജിൽ നിന്ന് ഒഴിവാക്കുന്നു (അത് വീണ്ടും വരാതിരിക്കാൻ)
                        edit_message_text(chat_id, message_id, f"✅ Selected Option: **{data}**")
                        
                        # യൂസറിന്റെ സ്റ്റേറ്റ് സെറ്റ് ചെയ്യുന്നു
                        user_states[user_id] = data
                        
                        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={
                            "callback_query_id": cq_id, 
                            "text": f"Activated: {data}"
                        })
                        
                        # ഓരോ ഫീച്ചറിനും അനുസരിച്ചുള്ള നിർദ്ദേശങ്ങൾ മാത്രം നൽകുന്നു
                        responses = {
                            "thumb_extract": "🖼️ **Thumb Extractor** activated.\nNow send your video file to extract the thumbnail.",
                            "caption_edit": "✏️ **Caption Editor** activated.\nSend the new caption text you want to apply.",
                            "meta_edit": "📋 **Metadata Editor** activated.\nSend your file to edit metadata.",
                            "stream_map": "🔀 **Stream Mapper** activated.\nSend the file for stream mapping.",
                            "stream_remove": "❌ **Stream Remover** activated.\nSend the file to remove unwanted streams.",
                            "stream_extract": "📥 **Stream Extractor** activated.\nSend the file to extract streams.",
                            "video_trim": "✂️ **Video Trimmer** activated.\nSend your video first, then send start and end times (e.g., 00:10-01:00).",
                            "video_merge": "➕ **Video Merger** activated.\nSend the videos you want to merge one by one. Once finished, type /done.",
                            "remove_audio": "🔇 **Remove Audio** activated.\nSend the video to remove its audio track.",
                            "merge_AV": "🔀 **Merge Audio & Video** activated.\nSend the audio and video files.",
                            "audio_conv": "🎵 **Audio Converter** activated.\nSend your audio file to convert.",
                            "video_split": "✂️ **Videos Splitter** activated.\nSend the video file you want to split.",
                            "screenshots": "🖼️ **Screenshots** activated.\nSend the video to generate automated screenshots.",
                            "manual_shots": "📸 **Manual Shots** activated.\nSend the video and timestamps.",
                            "gen_sample": "📊 **Generate Sample** activated.\nSend the video to generate a short sample clip.",
                            "vid_to_audio": "🔊 **Video To Audio** activated.\nSend the video file to extract audio.",
                            "vid_optimize": "⚡ **Video Optimizer** activated.\nSend the video to optimize its size and quality.",
                            "sub_merge": "💬 **Subtitle Merger** activated.\nSend the subtitle file (.srt) and the video.",
                            "vid_conv": "🔄 **Video Converter** activated.\nSend the video file to convert format.",
                            "vid_rename": "✏️ **Video Renamer** activated.\nSend the new filename for your media.",
                            "media_info": "ℹ️ **Media Information** activated.\nSend the file to fetch full media details.",
                            "create_archive": "📦 **Create Archive** activated.\nSend files to pack them into a zip archive."
                        }
                        
                        reply_text = responses.get(data, f"✅ You selected option: **{data}**")
                        send_message(chat_id, reply_text)
                            
        except Exception as e:
            print(f"Polling Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))).start()
    main()
