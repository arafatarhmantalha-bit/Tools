import os
import random
import string
import yt_dlp

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN2")

# -------- PASSWORD GENERATOR --------
def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(chars) for _ in range(10))


# -------- START MENU --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("📥 Downloader", callback_data="downloader")],
        [InlineKeyboardButton("🔐 Password Generator", callback_data="password")],
        [InlineKeyboardButton("🔎 Username Checker", callback_data="username")]
    ]

    text = "🤖 *Multi Tool Telegram Bot*\n\nChoose a tool:"

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# -------- BUTTON HANDLER --------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "password":

        password = generate_password()

        await query.edit_message_text(
            f"🔐 *Generated Password:*\n\n`{password}`",
            parse_mode="Markdown"
        )

    elif data == "username":

        await query.edit_message_text(
            "🔎 Send me a username to check.\n\nExample:\n`safi_bot`",
            parse_mode="Markdown"
        )

        context.user_data["check_username"] = True

    elif data == "downloader":

        await query.edit_message_text(
            "📥 Send a video link.\n\nSupported:\nYouTube / TikTok / Instagram"
        )

        context.user_data["download"] = True


# -------- MESSAGE HANDLER --------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    # USERNAME CHECK
    if context.user_data.get("check_username"):

        username = text.replace("@", "")

        try:
            chat = await context.bot.get_chat(f"@{username}")
            await update.message.reply_text("❌ Username already taken.")
        except:
            await update.message.reply_text("✅ Username available!")

        context.user_data["check_username"] = False

    # DOWNLOADER
    elif context.user_data.get("download"):

        url = text

        await update.message.reply_text("⏳ Downloading...")

        ydl_opts = {
            "format": "best",
            "outtmpl": "video.%(ext)s"
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            for file in os.listdir():
                if file.startswith("video"):
                    await update.message.reply_video(open(file, "rb"))
                    os.remove(file)

        except:
            await update.message.reply_text("❌ Download failed.")

        context.user_data["download"] = False


# -------- MAIN --------
def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buttons))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()