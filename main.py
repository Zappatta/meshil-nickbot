import sqlite3
import os
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging

# Get the bot token from the environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize the SQLite database
conn = sqlite3.connect('nicknames.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS nicknames
                  (nickname TEXT, username TEXT)''')
conn.commit()

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Use /register <nickname> to register a nickname and /whois <nickname> to find out who registered it.')

def register(update: Update, context: CallbackContext) -> None:
    """Register a nickname for a user."""
    user = update.message.from_user
    if len(context.args) != 1:
        update.message.reply_text('Usage: /register <nickname>')
        return

    nickname = context.args[0].lower()
    cursor.execute('INSERT INTO nicknames (nickname, username) VALUES (?, ?)', (nickname, user.username))
    conn.commit()

    update.message.reply_text(f'Nickname "{nickname}" registered successfully!')

def whois(update: Update, context: CallbackContext) -> None:
    """Identify the user who registered a nickname."""
    if len(context.args) != 1:
        update.message.reply_text('Usage: /whois <nickname>')
        return

    nickname = context.args[0].lower()
    cursor.execute('SELECT nickname, username FROM nicknames WHERE nickname LIKE ?', (nickname + '%',))
    rows = cursor.fetchall()

    if not rows:
        update.message.reply_text(f'No one has registered a nickname starting with "{nickname}".')
    else:
        response = ""
        for row in rows:
            response += f'Nickname "{row[0]}" is registered by @{row[1]}\n'
        update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN)

def main() -> None:
    """Start the bot."""
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("register", register))
    dispatcher.add_handler(CommandHandler("whois", whois))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()