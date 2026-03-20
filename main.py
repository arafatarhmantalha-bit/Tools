import os
import telebot
import asyncio
from telebot import types
from edge_tts import Communicate

# Railway Token (Environment variable)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# User preference memory
user_prefs = {}

# Voice mapping (Best realistic voices)
VOICES = {
    "bn_male": "bn-IN-BashkarNeural",      # Natural deep Bangla male (India)
    "bn_female": "bn-IN-TanishaaNeural",   # Best natural female Bangla
    "en_male": "en-US-GuyNeural",          # Natural English male
    "en_female": "en-US-JennyNeural"       # Smooth English female
}

# /start or /help command
@bot.message_handler(commands=['start', 'help'])
def start_cmd(message):
    try:
        chat_id = message.chat.id

        # Language selection
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("1. Bangla 🇧🇩", callback_data="lang_bn")
        btn2 = types.InlineKeyboardButton("2. English 🇺🇸", callback_data="lang_en")
        markup.add(btn1, btn2)

        bot.send_message(chat_id, "Write Your Script 🤌\n\nSelect Language:", reply_markup=markup)
    except Exception as e:
        print(f"Start Error: {e}")
        bot.send_message(message.chat.id, "😔 Error while starting, try again.")

# Callback handler (Language + Gender selection)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data

    try:
        if data.startswith("lang_"):
            lang = data.split("_")[1]
            user_prefs[chat_id] = {"lang": lang}

            # Gender selection
            markup = types.InlineKeyboardMarkup(row_width=2)
            g_btn1 = types.InlineKeyboardButton("Male 🧔", callback_data=f"gender_{lang}_male")
            g_btn2 = types.InlineKeyboardButton("Female 👩", callback_data=f"gender_{lang}_female")
            markup.add(g_btn1, g_btn2)

            bot.edit_message_text(
                "Select Gender:",
                chat_id,
                call.message.message_id,
                reply_markup=markup
            )

        elif data.startswith("gender_"):
            parts = data.split("_")
            lang, gender = parts[1], parts[2]
            voice_key = f"{lang}_{gender}"

            # Save final voice selection
            user_prefs[chat_id] = VOICES[voice_key]

            bot.edit_message_text(
                f"✅ Settings Saved!\n\nNow send me any text to convert 🎙️",
                chat_id,
                call.message.message_id
            )

    except Exception as e:
        print(f"Callback Error: {e}")
        bot.send_message(chat_id, "⚠️ Something went wrong, please try /start again.")

# Text handler for TTS
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    text = message.text

    try:
        # Check if user selected language/gender
        if chat_id not in user_prefs or isinstance(user_prefs[chat_id], dict):
            bot.reply_to(message, "Age /start likhe Language ar Gender select koro bro!")
            return

        selected_voice = user_prefs[chat_id]
        file_name = f"tts_{chat_id}.mp3"

        temp_msg = bot.send_message(chat_id, "⏳ Generating Audio...")

        async def create_audio():
            communicate = Communicate(text, selected_voice)
            await communicate.save(file_name)

        # Create an event loop safely
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(create_audio())

        with open(file_name, 'rb') as audio:
            bot.send_audio(chat_id, audio, caption="🎧 𝘾𝙧𝙚𝙖𝙩𝙚𝙙 𝘽𝙮 | 𝙎𝙖𝙖𝙁𝙚 🖤")

        bot.delete_message(chat_id, temp_msg.message_id)
        if os.path.exists(file_name):
            os.remove(file_name)

    except Exception as e:
        print(f"TTS Error: {e}")
        bot.send_message(chat_id, "😔 Voice generate korte problem hoyese, abar try koro bro.")

# 🔥 Start the bot
if __name__ == "__main__":
    print("✅ Bot is running...")
    bot.infinity_polling(timeout=60, long_polling_timeout=30)
