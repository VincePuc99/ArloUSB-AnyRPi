from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# Argument Parser for Token and CHATID
parser = argparse.ArgumentParser()
parser.add_argument('api_token', type=str, help='Telegram API token')
parser.add_argument('chat_id', type=str, help='Telegram chat ID')
args = parser.parse_args()

# Bot Init
TOKEN = args.api_token
CHATID = args.chat_id
DIR = "/mnt/ArloExposed/arlo/000000"

##################################################### DM

async def ignore_private_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type == 'private':
        return

##################################################### Arlo

import os
import hashlib

def calculate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

async def load_arlo(context):
    log_file_path = os.path.join(os.path.dirname(__file__), "mp4_hashes.log") #LogFile for hashes
    
    if os.path.exists(log_file_path):
        with open(log_file_path, "r") as log_file:
            existing_hashes = set(line.strip() for line in log_file)
    else:
        existing_hashes = set()

    with open(log_file_path, "a") as log_file:
        for filename in os.listdir(DIR):
            if filename.endswith(".mp4"): 
                file_path = os.path.join(DIR, filename)
                file_hash = calculate_file_hash(file_path)
                
                if file_hash not in existing_hashes: #hash non presente
                    await context.bot.send_video(chat_id=CHATID, video=file_path)

                    log_file.write(f"{file_hash}\n")
                    existing_hashes.add(file_hash)  

#####################################################

if __name__ == '__main__':
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE, ignore_private_messages))

    job_queue = application.job_queue
    job_queue.run_repeating(load_arlo, 20, first=1, name="Arlo")

    application.run_polling()
