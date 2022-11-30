#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import Update
from telegram.ext import CallbackContext, Updater, CommandHandler, Filters, MessageHandler

import os
import logging
import re
import requests
import json
import random
import mysql.connector

DBHOST = "localhost"
DBUSER = "honecker"
DBNAME = "honeckerdb"
DBPASSWORD = os.environ.get('DBPASSWORD')
SALAISUUS = os.environ.get('SALAISUUS')


# TODO: Make me a database
quotes = {} # { str : list[str] }

def dbtest(update: Update, context: CallbackContext):
    cursor = db.cursor()
    tuloste = str(cursor.execute("SHOW TABLES"))
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=tuloste)

def initdb():
    return mysql.connector.connect(
        host = DBHOST,
        user = DBUSER,
        password = DBPASSWORD,
        database = DBNAME
        )

#########
# QUOTE #
######################################################################################
# TODO: use database
def save_quote(name : str, quote : str):
    global quotes
    if not name in quotes:
        quotes[name] = [quote]
    else:
        quotes[name].append(quote)

# TODO: use database
def get_quote(name : str) -> str:
    global quotes
    if not name in quotes:
        return f"No quotes exist for {name}"
    else:
        return random.choice(quotes[name])

def add_quote(update: Update, context: CallbackContext):
    if len(context.args) < 2:
            context.bot.sendMessage(chat_id=update.message.chat.id, text='Usage: /addquote <name> <quote>')
    else:
        name = context.args[0].strip('@')
        quote = ' '.join(context.args[1:])
        if quote[0] == '"' and quote[len(quote) - 1] == '"':
            quote = quote[1:len(quote) - 1]
    save_quote(name, quote)
    context.bot.sendMessage(chat_id=update.message.chat.id, text='Quote saved!') # maybe not necessary to inform of success

def quote(update: Update, context: CallbackContext):
        name = context.args[0].strip('@')
        quote = get_quote(name)
        formated_quote = f'"{quote}" - {name}'
        context.bot.sendMessage(chat_id=update.message.chat.id, text=formated_quote)

######################################################################################

def arvon_paasihteeri(update: Update, context: CallbackContext):
    noppa = random.randint(0, 9)
    if noppa == 0:
	    paasihteeri="Politbyroo hyväksyy"
    elif noppa == 1:
        paasihteeri="...huh, anteeksi, torkahdin hetkeksi, kysyisitkö uudestaan?"
    else:
	    paasihteeri="SIPERIAAN!"
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=paasihteeri)

def main():
    global quotes
    global db
    global cursor
    db = initdb()
    cursor = db.cursor()
    updater = Updater(SALAISUUS, use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    honecker_re = re.compile(r'arvon pääsihteeri', flags=re.IGNORECASE)

    handlers = []
    handlers.append(CommandHandler("addquote", add_quote))
    handlers.append(CommandHandler("quote", quote))
    handlers.append(CommandHandler("dbtest", dbtest))
    handlers.append(MessageHandler(Filters.regex(honecker_re), arvon_paasihteeri))

    for handler in handlers:
        dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()

main()
