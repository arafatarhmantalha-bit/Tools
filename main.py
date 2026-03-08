import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# store last user image
USER_IMAGES = {}


# ---------------- START COMMAND ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Send me a photo and I will help you edit it!\n\n"
        "Available tools:\n"
        "• Remove Background\n"
        "• Cartoon Effect\n"
        "• Quality Enhance\n"
        "• Resize Image"
    )


# ---------------- RECEIVE PHOTO ----------------
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]
    file = await photo.get_file()

    file_path = f"{update.message.from_user.id}_image.jpg"
    await file.download_to_drive(file_path)

    USER_IMAGES[update.message.from_user.id] = file_path

    keyboard = [
        [InlineKeyboardButton("🧼 Remove Background", callback_data="remove_bg")],
        [InlineKeyboardButton("🎨 Cartoon Effect", callback_data="cartoon")],
        [InlineKeyboardButton("✨ Quality Enhance", callback_data="enhance")],
        [InlineKeyboardButton("🔲 Resize Image", callback_data="resize")],
    ]

    await update.message.reply_text(
        "🖼 Choose what you want to do with this image:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ---------------- BUTTON HANDLER ----------------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    if user_id not in USER_IMAGES:
        await query.edit_message_text("❌ Please send a photo first.")
        return

    image_path = USER_IMAGES[user_id]

    try:
        if query.data == "remove_bg":
            await remove_background(query, image_path)

        elif query.data == "cartoon":
            await cartoon_effect(query, image_path)

        elif query.data == "enhance":
            await enhance_image(query, image_path)

        elif query.data == "resize":
            await resize_image(query, image_path)

    except Exception as e:
        await query.message.reply_text("❌ Image processing failed.")


# ---------------- REMOVE BACKGROUND ----------------
async def remove_background(query, image_path):

    with open(image_path, "rb") as f:
        output = remove(f.read())

    output_path = "no_bg.png"

    with open(output_path, "wb") as out:
        out.write(output)

    await query.message.reply_photo(open(output_path, "rb"))


# ---------------- CARTOON EFFECT ----------------
async def cartoon_effect(query, image_path):

    img = cv2.imread(image_path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)

    edges = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        9, 9
    )

    color = cv2.bilateralFilter(img, 9, 300, 300)

    cartoon = cv2.bitwise_and(color, color, mask=edges)

    output_path = "cartoon.jpg"
    cv2.imwrite(output_path, cartoon)

    await query.message.reply_photo(open(output_path, "rb"))


# ---------------- QUALITY ENHANCE ----------------
async def enhance_image(query, image_path):

    img = Image.open(image_path)

    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2)

    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    output_path = "enhanced.jpg"
    img.save(output_path)

    await query.message.reply_photo(open(output_path, "rb"))


# ---------------- RESIZE IMAGE ----------------
async def resize_image(query, image_path):

    img = Image.open(image_path)

    img = img.resize((1024, 1024))

    output_path = "resized.jpg"
    img.save(output_path)

    await query.message.reply_photo(open(output_path, "rb"))


# ---------------- MAIN FUNCTION ----------------
def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot running...")

    app.run_polling()


if __name__ == "__main__":
    main()
