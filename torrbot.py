# TODO Default n for downloads if first argument is not numeric
# TODO Possibility to cancel download

import yaml
import logging
import pandas as pd
from transmission_rpc import Client

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

from scraper import search_piratebay

# Load config file
with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    token = config['token']
    username = config['username']
    password = config['password']
    host = config['host']
    port = config['port']

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def pirate_search(update, context):
    """Usage /piratesearch n query"""
    n = int(context.args[0])
    text = ' '.join(context.args[1:])
    results = search_piratebay(text)
    if len(results):
        context.user_data['query'] = results[:n].to_json()

        results_str = results[['Name', 'Size', 'Seeders']][:n].to_string(justify='center', max_colwidth=30)
        results_str = '```' + results_str + '```'
        context.bot.send_message(chat_id=update.effective_chat.id, text=results_str, parse_mode=ParseMode.MARKDOWN)
    else:
        update.message.reply_text('No results found. Please try again.')


def download(update, context):
    """Usage: /download idx"""
    idx = context.args[0]

    # Load value
    try:
        query_df = pd.read_json(context.user_data.get("query", None))

        if query_df is not None:
            link = query_df.loc[int(idx), 'Link']
            send_to_transmission(link)
            name = query_df.loc[int(idx), 'Name']
            update.message.reply_text(f'Starting download: {name}')

    except:
        update.message.reply_text('Ooops, something went wrong!')


def send_to_transmission(link):
    """Sends a link to the transmission rpc client adding it to the downloads."""
    c = Client(host=host, port=port, username=username, password=password)
    c.add_torrent(link)


def cancel_torrent():
    # TODO
    pass


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('piratesearch', pirate_search))
    dp.add_handler(CommandHandler('download', download))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
