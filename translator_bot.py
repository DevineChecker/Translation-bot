import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import pytesseract
from PIL import Image
from googletrans import Translator
import os
from unidecode import unidecode

# === CONFIG ===
BOT_TOKEN = "7619644829:AAGA-Q6ZDWq5HZNIVjLLbCy-sieK5uKeB9g"
bot = telebot.TeleBot(BOT_TOKEN)
translator = Translator()

# Store user language preferences
user_lang = {}

# /start command
@bot.message_handler(commands=['start'])
def start(message: Message):
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton("🇬🇧 English", callback_data="setlang_en"),
        InlineKeyboardButton("🇮🇳 Hindi", callback_data="setlang_hi"),
        InlineKeyboardButton("🇮🇳 Hinglish", callback_data="setlang_hinglish"),
        InlineKeyboardButton("🇫🇷 French", callback_data="setlang_fr"),
        InlineKeyboardButton("🇪🇸 Spanish", callback_data="setlang_es"),
        InlineKeyboardButton("🇩🇪 German", callback_data="setlang_de"),
    )
    bot.reply_to(message,
        "👋 Hi! Send me a sticker/photo with text and I’ll translate it.\n\n"
        "📌 Pick your translation language below or use `/setlang <code>` manually.\n"
        "ℹ️ Use /langcodes for the full list.",
        reply_markup=markup
    )

# Handle button presses
@bot.callback_query_handler(func=lambda call: call.data.startswith("setlang_"))
def callback_setlang(call):
    code = call.data.replace("setlang_", "")
    user_lang[call.message.chat.id] = code
    bot.answer_callback_query(call.id, f"✅ Language set to {code.upper()}")
    bot.send_message(call.message.chat.id, f"✅ Translation language set to `{code}`", parse_mode="Markdown")

# /setlang command (manual)
@bot.message_handler(commands=['setlang'])
def set_language(message: Message):
    try:
        code = message.text.split()[1].lower()
        user_lang[message.chat.id] = code
        bot.reply_to(message, f"✅ Language set to `{code}`", parse_mode="Markdown")
    except IndexError:
        bot.reply_to(message, "❌ Please provide a language code.\nExample: `/setlang hi` or `/setlang hinglish`", parse_mode="Markdown")

# /langcodes command
@bot.message_handler(commands=['langcodes'])
def langcodes(message: Message):
    codes = """
🌍 **Language Codes (ISO 639-1)**

- en = English  
- hi = Hindi  
- hinglish = Hindi text in English letters  
- ur = Urdu  
- ar = Arabic  
- fr = French  
- es = Spanish  
- de = German  
- ru = Russian  
- zh-cn = Chinese (Simplified)  
- ja = Japanese  
- ko = Korean  
- it = Italian  
- pt = Portuguese  
- bn = Bengali  
- tr = Turkish  

Use `/setlang <code>` or buttons to change language.
"""
    bot.reply_to(message, codes, parse_mode="Markdown")

# Handle stickers/photos
@bot.message_handler(content_types=['sticker', 'photo'])
def handle_sticker_or_photo(message: Message):
    file_id = message.sticker.file_id if message.content_type == 'sticker' else message.photo[-1].file_id

    if file_id:
        file_info = bot.get_file(file_id)
        downloaded = bot.download_file(file_info.file_path)

        filename = f"temp_{message.chat.id}.png"
        with open(filename, "wb") as f:
            f.write(downloaded)

        # OCR
        img = Image.open(filename)
        extracted_text = pytesseract.image_to_string(img)

        if extracted_text.strip() == "":
            bot.reply_to(message, "⚠️ No text detected in this sticker/image.")
        else:
            target_lang = user_lang.get(message.chat.id, "en")  # default English

            if target_lang == "hinglish":
                # Step 1: Translate to Hindi
                translated_hi = translator.translate(extracted_text, dest="hi").text
                # Step 2: Convert to Hinglish
                hinglish_text = unidecode(translated_hi)

                bot.reply_to(
                    message,
                    f"🌍 **Detected Text:**\n`{extracted_text.strip()}`\n\n"
                    f"🔤 **Translated (HINGLISH):**\n`{hinglish_text}`",
                    parse_mode="Markdown"
                )
            else:
                translated = translator.translate(extracted_text, dest=target_lang)

                bot.reply_to(
                    message,
                    f"🌍 **Detected Text:**\n`{extracted_text.strip()}`\n\n"
                    f"🔤 **Translated ({target_lang.upper()}):**\n`{translated.text}`",
                    parse_mode="Markdown"
                )

        os.remove(filename)

# Run bot
print("🤖 Translator Bot Running...")
bot.infinity_polling()