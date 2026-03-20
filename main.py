import os
import telebot
from gtts import gTTS

# Railway theke token auto nibe
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Please Write Your Script.")

# Text to Speech function
@bot.message_handler(func=lambda message: True)
def generate_speech(message):
    user_text = message.text
    chat_id = message.chat.id

    try:
        # User ke wait korte bola
        temp_msg = bot.send_message(chat_id, "⏳ Generating audio...")

        # Text ke audio te convert kora (English e)
        tts = gTTS(text=user_text, lang='en')
        file_name = f"audio_{chat_id}.mp3"
        tts.save(file_name)

        # MP3 file send kora with caption
        with open(file_name, 'rb') as audio_file:
            bot.send_audio(
                chat_id, 
                audio_file, 
                caption="𝘾𝙧𝙚𝙖𝙩𝙚𝙙 𝘽𝙮 | 𝙎𝙖𝙖𝙁𝙚 🖤"
            )
        
        # Temp message delete kora and mp3 file delete kora (storage bachanar jonno)
        bot.delete_message(chat_id, temp_msg.message_id)
        os.remove(file_name)

    except Exception as e:
        bot.send_message(chat_id, "Sorry bro, ekta problem hoyese. Abar try koro.")
        print(f"Error: {e}")

print("Bot is successfully running...!")
bot.infinity_polling()
