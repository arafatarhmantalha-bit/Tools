import os
import telebot
import asyncio
from telebot import types
from edge_tts import Communicate
from collections import defaultdict
import time

BOT_TOKEN = os.environ.get('BOT_TOKEN')
OWNER_ID = int(os.environ.get('OWNER_ID', 0))  # Railway a OWNER_ID env variable set koro
bot = telebot.TeleBot(BOT_TOKEN)

user_prefs = {}
user_history = defaultdict(list)  # Last 5 texts per user
all_users = set()                  # Total user count

# Spam protection
user_last_request = {}
COOLDOWN_SECONDS = 5

VOICES = {
    "bnbd_male":   "bn-BD-PradeepNeural",
    "bnbd_female": "bn-BD-NabanitaNeural",
    "bnin_male":   "bn-IN-BashkarNeural",
    "bnin_female": "bn-IN-TanishaaNeural",
    "en_male":     "en-US-GuyNeural",
    "en_female":   "en-US-JennyNeural",
    "hi_male":     "hi-IN-MadhurNeural",
    "hi_female":   "hi-IN-SwaraNeural",
    "ur_male":     "ur-PK-AsadNeural",
    "ur_female":   "ur-PK-UzmaNeural"
}

LANG_LABELS = {
    "bnbd": "Bangla 🇧🇩 BD",
    "bnin": "Bangla 🇮🇳 IN",
    "en":   "English 🇺🇸",
    "hi":   "Hindi 🇮🇳",
    "ur":   "Urdu 🇵🇰"
}

GENDER_LABELS = {
    "male":   "Male 🧔",
    "female": "Female 👩"
}

SPEED_LABELS = {
    "slow":   "🐢 Slow",
    "normal": "🚶 Normal",
    "fast":   "⚡ Fast"
}

SPEED_RATES = {
    "slow":   "-20%",
    "normal": "+0%",
    "fast":   "+20%"
}

MAX_CHARS = 1000


def language_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("Bangla 🇧🇩 BD", callback_data="lang_bnbd")
    btn2 = types.InlineKeyboardButton("Bangla 🇮🇳 IN", callback_data="lang_bnin")
    btn3 = types.InlineKeyboardButton("English 🇺🇸",   callback_data="lang_en")
    btn4 = types.InlineKeyboardButton("Hindi 🇮🇳",     callback_data="lang_hi")
    btn5 = types.InlineKeyboardButton("Urdu 🇵🇰",      callback_data="lang_ur")
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup


def speed_markup():
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("🐢 Slow",   callback_data="speed_slow"),
        types.InlineKeyboardButton("🚶 Normal", callback_data="speed_normal"),
        types.InlineKeyboardButton("⚡ Fast",   callback_data="speed_fast")
    )
    return markup


# /start or /help
@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    try:
        all_users.add(message.chat.id)
        bot.send_message(
            message.chat.id,
            "Write Your Script 🤌\n\nSelect Language:",
            reply_markup=language_markup()
        )
    except Exception as e:
        print(f"Start Error: {e}")


# /change command
@bot.message_handler(commands=['change'])
def change_cmd(message):
    try:
        all_users.add(message.chat.id)
        bot.send_message(
            message.chat.id,
            "🔄 Change Voice\n\nSelect Language:",
            reply_markup=language_markup()
        )
    except Exception as e:
        print(f"Change Error: {e}")


# /myvoice command
@bot.message_handler(commands=['myvoice'])
def myvoice_cmd(message):
    try:
        chat_id = message.chat.id

        if chat_id not in user_prefs or isinstance(user_prefs[chat_id], dict):
            bot.reply_to(message, "⚠️ Tumi ekhono kono voice select koro nai.\n/start diye select koro.")
            return

        current_voice = user_prefs[chat_id]["voice"]
        current_speed = user_prefs[chat_id].get("speed", "normal")

        lang_key, gender_key = None, None
        for key, val in VOICES.items():
            if val == current_voice:
                parts = key.rsplit("_", 1)
                lang_key, gender_key = parts[0], parts[1]
                break

        bot.reply_to(
            message,
            f"🎙️ Current Voice:\n\n🌐 Language: {LANG_LABELS[lang_key]}\n👤 Gender: {GENDER_LABELS[gender_key]}\n⚡ Speed: {SPEED_LABELS[current_speed]}"
        )
    except Exception as e:
        print(f"MyVoice Error: {e}")


# /history command
@bot.message_handler(commands=['history'])
def history_cmd(message):
    try:
        chat_id = message.chat.id
        history = user_history[chat_id]

        if not history:
            bot.reply_to(message, "📭 Kono history nai ekhono.")
            return

        text = "📜 Last 5 Converted Texts:\n\n"
        for i, item in enumerate(reversed(history), 1):
            text += f"{i}. {item}\n\n"

        bot.reply_to(message, text)
    except Exception as e:
        print(f"History Error: {e}")


# /stats command (owner only)
@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    try:
        if message.chat.id != OWNER_ID:
            bot.reply_to(message, "⛔ Tumi ei command use korte parbe na.")
            return

        bot.reply_to(message, f"📊 Bot Stats:\n\n👥 Total Users: {len(all_users)}")
    except Exception as e:
        print(f"Stats Error: {e}")


# Callback — Language, Gender, Speed, Change Voice
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data

    try:
        if data.startswith("lang_"):
            lang = data.split("lang_")[1]
            user_prefs[chat_id] = {"lang": lang}

            markup = types.InlineKeyboardMarkup(row_width=2)
            g_btn1 = types.InlineKeyboardButton("Male 🧔",   callback_data=f"gender_{lang}_male")
            g_btn2 = types.InlineKeyboardButton("Female 👩", callback_data=f"gender_{lang}_female")
            markup.add(g_btn1, g_btn2)

            bot.edit_message_text(
                "Select Gender:",
                chat_id,
                call.message.message_id,
                reply_markup=markup
            )

        elif data.startswith("gender_"):
            parts = data.split("gender_")[1].rsplit("_", 1)
            lang, gender = parts[0], parts[1]

            # Temporarily save lang+gender, wait for speed
            user_prefs[chat_id] = {"lang": lang, "gender": gender}

            bot.edit_message_text(
                "Select Speed:",
                chat_id,
                call.message.message_id,
                reply_markup=speed_markup()
            )

        elif data.startswith("speed_"):
            speed = data.split("speed_")[1]

            prefs = user_prefs.get(chat_id, {})
            lang   = prefs.get("lang")
            gender = prefs.get("gender")

            if not lang or not gender:
                bot.send_message(chat_id, "⚠️ Kisu ekta problem hoyese, /start diye abar try koro.")
                return

            voice_key = f"{lang}_{gender}"
            user_prefs[chat_id] = {
                "voice": VOICES[voice_key],
                "speed": speed
            }

            bot.edit_message_text(
                f"✅ Settings Saved!\n\n🌐 Language: {LANG_LABELS[lang]}\n🎙️ Gender: {GENDER_LABELS[gender]}\n⚡ Speed: {SPEED_LABELS[speed]}\n\nNow send me any text to convert.",
                chat_id,
                call.message.message_id
            )

        elif data == "change_voice":
            bot.send_message(
                chat_id,
                "🔄 Change Voice\n\nSelect Language:",
                reply_markup=language_markup()
            )

    except Exception as e:
        print(f"Callback Error: {e}")


# Text → TTS
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    all_users.add(chat_id)

    # Spam / flood protection
    now = time.time()
    last = user_last_request.get(chat_id, 0)
    if now - last < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last))
        bot.reply_to(message, f"⏳ Ektu wait koro! {remaining} second pore abar try koro.")
        return
    user_last_request[chat_id] = now

    # Voice setup check
    prefs = user_prefs.get(chat_id)
    if not prefs or isinstance(prefs, dict) and "voice" not in prefs:
        bot.reply_to(message, "Age /start likhe Language ar Gender select koro bro!")
        return

    # Character limit
    if len(text) > MAX_CHARS:
        bot.reply_to(message, f"⚠️ Text onek boro! Maximum {MAX_CHARS} character er modhe rakho.")
        return

    selected_voice = prefs["voice"]
    selected_rate  = SPEED_RATES[prefs.get("speed", "normal")]
    file_name = f"tts_{chat_id}.mp3"

    try:
        temp_msg = bot.send_message(chat_id, "⏳ Generating Audio...")

        async def create_audio():
            communicate = Communicate(text, selected_voice, rate=selected_rate)
            await communicate.save(file_name)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(create_audio())
        loop.close()

        # Save to history (max 5)
        user_history[chat_id].append(text[:100] + ("..." if len(text) > 100 else ""))
        if len(user_history[chat_id]) > 5:
            user_history[chat_id].pop(0)

        # Change voice button
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔄 Change Voice", callback_data="change_voice"))

        with open(file_name, 'rb') as audio:
            bot.send_audio(
                chat_id,
                audio,
                caption="🎧 𝘾𝙧𝙚𝙖𝙩𝙚𝙙 𝘽𝙮 | 𝙎𝙖𝙖𝙁𝙚 🖤",
                reply_markup=markup
            )

        try:
            bot.delete_message(chat_id, temp_msg.message_id)
        except Exception as e:
            print(f"Ignored delete error: {e}")

        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as e:
        print(f"TTS Error: {e}")
        bot.send_message(chat_id, "😔 Error hoyese, abar try koro bro.")


if __name__ == "__main__":
    print("✅ Bot is running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
