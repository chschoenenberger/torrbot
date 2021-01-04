import logging
from telegram.ext import Updater, CommandHandler

from config_loader import load_config
from bot_commands import *

# Load config file
token, username, password, host, port = load_config()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    """Start the bot."""
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('piratesearch', pirate_search))
    dp.add_handler(CommandHandler('more', more))
    dp.add_handler(CommandHandler('download', download))
    dp.add_handler(CommandHandler('listtorrents', list_torrents))
    dp.add_handler(CommandHandler('deletealltorrents', delete_all_torrents))
    dp.add_handler(CommandHandler('deletetorrent', delete_torrent))

    # Start the Bot
    updater.start_polling()

    # Run the bot
    updater.idle()


if __name__ == '__main__':
    main()
