import os
import yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.error import BadRequest

# Settings
TOKEN = "8430109439:AAFEyhbGrAGbMJTA6xgPZZdVK-gmjz8aqCk" 
# Aapke channels update kar diye gaye hain
CHANNELS = ["@smartwaysbots", "@SmartWayes"] 

user_data = {}

async def is_subscribed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception:
            return False
    return True

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        keyboard = [
            [InlineKeyboardButton("Join Channel 1", url=f"https://t.me/smartwaysbots")],
            [InlineKeyboardButton("Join Channel 2", url=f"https://t.me/SmartWayes")],
            [InlineKeyboardButton("Check Membership ✅", callback_data="check_sub")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("⚠️ **Access Denied!**\n\nBot use karne ke liye hamare dono channels join karein.", reply_markup=reply_markup)
        return
    await update.message.reply_text("✅ Access Granted! YouTube link bhejein.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_subscribed(update, context):
        await start(update, context)
        return

    url = update.message.text
    if "youtube.com" in url or "youtu.be" in url:
        user_data[update.message.chat_id] = url
        keyboard = [
            [InlineKeyboardButton("720p", callback_data='best[height<=720][ext=mp4]/best[ext=mp4]/best')],
            [InlineKeyboardButton("480p", callback_data='best[height<=480][ext=mp4]/best[ext=mp4]/best')],
            [InlineKeyboardButton("Audio (MP3)", callback_data='bestaudio/best')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Quality select karein:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Sahi YouTube link bhejein.")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    
    if query.data == "check_sub":
        if await is_subscribed(update, context):
            await query.edit_message_text("Shukriya! Ab aap links bhej sakte hain.")
        else:
            await query.answer("Dono join nahi kiye!", show_alert=True)
        return

    url = user_data.get(chat_id)
    if not url: return

    msg = await query.edit_message_text("📥 Downloading... (Please wait)")
    
    try:
        output_tmpl = f'video_{chat_id}'
        
        ydl_opts = {
            'format': query.data,
            'outtmpl': output_tmpl,
            'max_filesize': 49 * 1024 * 1024, 
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if not os.path.exists(filename):
                filename = filename + ".mp4"

        await context.bot.send_video(chat_id=chat_id, video=open(filename, 'rb'), caption="Downloaded by SmartWays Bot")
        os.remove(filename)
        await msg.delete()

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Error: Video 50MB se badi ho sakti hai ya download limit hit ho gayi hai.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
