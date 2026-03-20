import os
import telebot
from gtts import gTTS

# Railway variables theke token nibe
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
        temp_msg = bot.send_message(chat_id, "⏳ আপনার অডিও তৈরি হচ্ছে...")

        # ekhane lang='bn' deya hoyese jate Bangla speech hoy
        tts = gTTS(text=user_text, lang='bn') 
        file_name = f"audio_{chat_id}.mp3"
        tts.save(file_name)

        # MP3 file send kora with caption
        with open(file_name, 'rb') as audio_file:
            bot.send_audio(
                chat_id, 
                audio_file, 
                caption="𝘾𝙧𝙚𝙖𝙩𝙚𝙙 𝘽𝙮 | 𝙎𝙖𝙖𝙁𝙚 🖤"
            )
        
        # Temp message delete kora and local file remove kora
        bot.delete_message(chat_id, temp_msg.message_id)
        os.remove(file_name)

    except Exception as e:
        bot.send_message(chat_id, "দুঃখিত, কোনো সমস্যা হয়েছে। আবার চেষ্টা করুন।")
        print(f"Error: {e}")

print("Bangla TTS Bot is running...")
bot.infinity_polling()
