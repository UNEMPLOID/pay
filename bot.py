#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import re
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
import pymongo
from luhn import verify

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
client = pymongo.MongoClient(os.getenv("mongodb+srv://admin22:admin22@cluster0.9lqp0ci.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"))  # MONGO DB LINK
db = client.credit_cards

# Configuration
developers = ['5606990991']
tk = "7234133234:AAEXdgCkqsv9lAlQ6Y4H2YOeeXh5yWBe8ac"
mode = "prod"
posting_channel = "-1002194819681"

def run(updater):
    if mode == "dev":
        updater.start_polling()
        updater.idle()
    elif mode == "prod":
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("ccscra")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=tk)
        updater.bot.set_webhook(f"https://{HEROKU_APP_NAME}.herokuapp.com/{tk}")
    else:
        sys.exit()

@run_async
def start(update, context):
    update.message.reply_text("This CC Scraper has been started successfully | Developed by [𝕭𝖔𝕲] Emilio")

@run_async
def extrct(update, context):
    gex = ['-11111111111']  # To exclude groups from scraping

    try:
        chat_id = str(update.message.chat_id)
    except Exception as e:
        logger.error(f"Error extracting chat_id: {e}")
        return

    if chat_id not in gex and chat_id == posting_channel:
        rawdata = update.message.text

        filtron = "[0-9]{16}[|][0-9]{1,2}[|][0-9]{2,4}[|][0-9]{3}"
        filtroa = "[0-9]{15}[|][0-9]{1,2}[|][0-9]{2,4}[|][0-9]{4}"
        detectavisa = "[0-9]{16}"
        detectamex = "[0-9]{15}"

        try:
            sacanumvisa = re.findall(detectavisa, rawdata)
            carduno = sacanumvisa[0] if sacanumvisa else None
            tipocard = str(carduno[0:1]) if carduno else ""

            if not carduno:
                sacanumamex = re.findall(detectamex, rawdata)
                carduno = sacanumamex[0] if sacanumamex else None
                tipocard = str(carduno[0:1]) if carduno else ""

            if tipocard == "3":
                x = re.findall(filtroa, rawdata)[0] if re.findall(filtroa, rawdata) else None
            elif tipocard in "456":
                x = re.findall(filtron, rawdata)[0] if re.findall(filtron, rawdata) else None
            else:
                x = None

            if x:
                card_number = x.split("|")[0]
                check_if_cc = db.credit_card.find_one({'cc_num': card_number})
                existe = check_if_cc is not None

                if not existe and verify(card_number):
                    cc_data = {
                        "bin": card_number[:6],
                        "cc_full": x,
                        "cc_num": card_number
                    }
                    db.credit_card.insert_one(cc_data)

                    card_send_formatted = f'CC: {x}'
                    context.bot.send_message(chat_id=posting_channel, text=card_send_formatted, parse_mode='HTML')

        except Exception as e:
            logger.error(f"Error processing message: {e}")

def main():
    updater = Updater(tk, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, extrct))
    run(updater)

if __name__ == '__main__':
    main()
