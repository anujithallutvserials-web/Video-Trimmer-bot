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

user_states = {}       # യൂസർ ഇപ്പോൾ ഏത് മോഡിലാണ് എന്ന് അറിയാൻ
user_merge_files = {}  # മെർജ് ചെയ്യാൻ അയക്കുന്ന വീഡിയോകൾ സേവ് ചെയ്തുവെക്കാൻ

def main():
    offset = 0
    print("Telegram Bot Started with Clean State Management!")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}&timeout=30"
            response = requests.get(url).json()
            
            if response.get("ok"):
                for update in response.get("result", []):
                    offset = update["update_id"] + 1
                    
                    # 1. Handle Messages
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
                            user_states[user_id] = None
                            user_merge_files[user_id] = []
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
                            send_message(chat_id, "⚙️ **Bot Settings Menu**\n\nConfigure your preferences below:", reply_markup=get_video_menu())
                        
                        # /done Command (പ്രത്യേകിച്ച് Video Merger-ന് ശേഷം പ്രോസസ്സ് ചെയ്യാൻ)
                        elif text.startswith("/done"):
                            current_state = user_states.get(user_id)
                            if current_state == "video_merge":
                                files_count = len(user_merge_files.get(user_id, []))
                                if files_count > 0:
                                    send_message(chat_id, f"⚙️ Processing **Video Merger** with {files_count} videos. Please wait...")
                                    # ഇവിടെ നിങ്ങളുടെ വീഡിയോ മെർജ് ചെയ്യുന്ന പൈത്തൺ കോഡ് (FFmpeg) നൽകാം
                                    time.sleep(2)
                                    send_message(chat_id, "✅ **Videos merged successfully!** (Here is your output video)")
                                    # പ്രോസസ്സ് കഴിഞ്ഞു സ്റ്റേറ്റ് ക്ലിയർ ചെയ്യുന്നു, ഇനി മെനു വീണ്ടും വരുത്താം
                                    user_states[user_id] = None
                                    user_merge_files[user_id] = []
                                    send_message(chat_id, "🎬 Send a new video or type /settings to continue:", reply_markup=get_video_menu())
                                else:
                                    send_message(chat_id, "⚠️ No videos found to merge. Please send videos first.")
                            else:
                                send_message(chat_id, "⚠️ No active task found to finish.")
                                user_states[user_id] = None
                                send_message(chat_id, "🎬 Choose an option:", reply_markup=get_video_menu())
                        
                        # Handle Videos or Documents
                        elif "video" in msg or "document" in msg:
                            current_state = user_states.get(user_id)
                            
                            # സ്റ്റേറ്റ് ഉണ്ടെങ്കിൽ (ഉദാ: Video Merger സെലക്ട് ചെയ്തിട്ടുണ്ടെങ്കിൽ)
                            if current_state == "video_merge":
                                file_id = msg.get("video", {}).get("file_id") or msg.get("document", {}).get("file_id")
                                if user_id not in user_merge_files:
                                    user_merge_files[user_id] = []
                                user_merge_files[user_id].append(file_id)
                                send_message(chat_id, f"📥 Video added for **Video Merger** (Total: {len(user_merge_files[user_id])}). Send more or type `/done` to process.")
                                continue
                            
                            elif current_state == "video_trim":
                                send_message(chat_id, "✂️ Video received for **Video Trimmer**. Now send start and end times (e.g., 00:00-01:00).")
                                # പ്രോസസ്സ് കഴിഞ്ഞ ശേഷം സ്റ്റേറ്റ് ക്ലിയർ ചെയ്യാൻ താഴെ കൊടുക്കാം
                                continue
                                
                            # സ്റ്റേറ്റ് ഒന്നും സെലക്ട് ചെയ്തിട്ടില്ലെങ്കിൽ മാത്രം പുതിയ വീഡിയോയ്ക്ക് 22 ബട്ടണുകൾ കാണിക്കുക
                            send_message(chat_id, "🎬 **Video received successfully!** Please choose your required option from below:", reply_markup=get_video_menu())
                    
                    # 2. Handle Callback Queries (Button Clicks)
                    elif "callback_query" in update:
                        cq = update["callback_query"]
                        cq_id = cq["id"]
                        chat_id = cq["message"]["chat"]["id"]
                        message_id = cq["message"]["message_id"]
                        user_id = cq["from"]["id"]
                        data = cq["data"]
                        
                        # പ്രധാന മാറ്റം: ബട്ടൺ ക്ലിക്ക് ചെയ്യുമ്പോൾ ആ മെസ്സേജിലെ 22 ബട്ടണുകൾ പൂർണ്ണമായി മാറ്റി താഴെ പറയുന്ന മെസ്സേജ് മാത്രം കാണിക്കുന്നു
                        edit_message_text(chat_id, message_id, f"✅ Selected Option: **{data}**")
                        
                        # യൂസറിന്റെ സ്റ്റേറ്റ് അപ്ഡേറ്റ് ചെയ്യുന്നു
                        user_states[user_id] = data
                        if data == "video_merge":
                            user_merge_files[user_id] = [] # ലിസ്റ്റ് ക്ലിയർ ചെയ്യുന്നു
                        
                        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery", json={
                            "callback_query_id": cq_id, 
                            "text": f"Activated: {data}"
                        })
                        
                        # ഓരോ ഫീച്ചറിനും അനുസരിച്ചുള്ള നിർദ്ദേശങ്ങൾ
                        responses = {
                            "thumb_extract": "🖼️ **Thumb Extractor** activated.\nSend your video file to extract the thumbnail.",
                            "caption_edit": "✏️ **Caption Editor** activated.\nSend the new caption text.",
                            "meta_edit": "📋 **Metadata Editor** activated.\nSend your file to edit metadata.",
                            "stream_map": "🔀 **Stream Mapper** activated.\nSend the file for stream mapping.",
                            "stream_remove": "❌ **Stream Remover** activated.\nSend the file to remove unwanted streams.",
                            "stream_extract": "📥 **Stream Extractor** activated.\nSend the file to extract streams.",
                            "video_trim": "✂️ **Video Trimmer** activated.\nSend start and end times (e.g., 00:00-01:00).",
                            "video_merge": "➕ **Video Merger** activated.\nSend the videos one by one. Once all videos are sent, type `/done` to start merging.",
                            "remove_audio": "🔇 **Remove Audio** activated.\nSend the video file.",
                            "merge_AV": "🔀 **Merge Audio & Video** activated.\nSend audio and video files.",
                            "audio_conv": "🎵 **Audio Converter** activated.\nSend your audio file.",
                            "video_split": "✂️ **Videos Splitter** activated.\nSend the video file to split.",
                            "screenshots": "🖼️ **Screenshots** activated.\nSend the video file.",
                            "manual_shots": "📸 **Manual Shots** activated.\nSend the video and timestamps.",
                            "gen_sample": "📊 **Generate Sample** activated.\nSend the video file.",
                            "vid_to_audio": "🔊 **Video To Audio** activated.\nSend the video file.",
                            "vid_optimize": "⚡ **Video Optimizer** activated.\nSend the video file.",
                            "sub_merge": "💬 **Subtitle Merger** activated.\nSend subtitle file and video.",
                            "vid_conv": "🔄 **Video Converter** activated.\nSend the video file.",
                            "vid_rename": "✏️ **Video Renamer** activated.\nSend the new filename.",
                            "media_info": "ℹ️ **Media Information** activated.\nSend the file.",
                            "create_archive": "📦 **Create Archive** activated.\nSend files to archive."
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
