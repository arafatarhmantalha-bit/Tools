import os
import telebot
import asyncio
from edge_tts import Communicate

# Railway variables theke token nibe
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Bangla Male Voice select kora holo
# bn-IN-BashkarNeural holo cheler voice
VOICE = "bn-IN-BashkarNeural"

# /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Please Write Your Script.")

# Text to Speech function
@bot.message_handler(func=lambda message: True)
def generate_speech(message):
    user_text = message.text
    chat_id = message.chat.id
    file_name = f"audio_{chat_id}.mp3"

    try:
        # User ke wait korte bola
        temp_msg = bot.send_message(chat_id, "⏳ Please wait , Voice Creating...")

        # Async function audio create korar jonno
        async def make_audio():
            communicate = Communicate(user_text, VOICE)
            await communicate.save(file_name)

        # Run the async function
        asyncio.run(make_audio())

        # MP3 file send kora with caption
        with open(file_name, 'rb') as audio_file:
            bot.send_audio(
                chat_id, 
                audio_file, 
                caption="Created by Grok Ai."
            )
        
        # Temp message delete kora and file remove kora
        bot.delete_message(chat_id, temp_msg.message_id)
        os.remove(file_name)

    except Exception as e:
        bot.send_message(chat_id, "দুঃখিত, কোনো সমস্যা হয়েছে। আবার চেষ্টা করুন।")
        print(f"Error: {e}")

print("Bangla Male Voice Bot is running...")
bot.infinity_polling()
