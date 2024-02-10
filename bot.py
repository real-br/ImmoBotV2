#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.


# https://github.com/python-telegram-bot/python-telegram-bot/


import logging
from VastgoedScraper import VastgoedScraper
from Century21Scraper import Century21Scraper

# from EraScraper import EraScraper -> no longer working

from LecobelScraper import LecobelScraper

from interaction import (
    conversation_handler,
)
import config
import glob

from telegram import Update
from telegram.ext import (
    Application,
    CallbackContext,
)
from telegram.error import BadRequest


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
TOKEN = config.CHATBOT_TOKEN
if TOKEN == None:
    print(glob.glob("*"))
    print(
        "No telegram API token found; set environment variable 'TELEGRAM_TOKEN' or create .env file for Docker."
    )
    exit(1)

scrapers = [LecobelScraper, Century21Scraper]

STATES_VASTGOED = 0


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def vastgoed(update: Update, context: CallbackContext) -> None:
    # print(update._effective_chat.id)
    # update.message.reply_text("Immokantoor:",reply_markup=ReplyKeyboardMarkup(
    #         [[scraper.get_scraper_name() for scraper in scrapers]], one_time_keyboard=True))

    # return STATES_VASTGOED
    for scraper in scrapers:
        for listing in scraper.get_saved_listings():
            caption, img = generate_saved_listing_response(
                scraper.get_scraper_name(), listing
            )
            # context.bot.send_photo(chat_id=OWN_CHAT_ID, photo=img, caption=caption, parse_mode='Markdown')
            try:
                context.bot.send_photo(
                    chat_id=config.OWN_CHAT_ID,
                    photo=img,
                    caption=caption,
                    parse_mode="Markdown",
                )
            except BadRequest as e:
                context.bot.send_message(
                    chat_id=config.OWN_CHAT_ID, text=caption, parse_mode="Markdown"
                )


def generate_saved_listing_response(immo_name, listing):
    price = listing["price"]
    price = f"€{price}" if price is not None else "-"
    caption = f"🌐 [{immo_name.capitalize()}]({listing['url']})\n🏠 {listing['address']}\n💰 {price}"
    img_url = listing["img_url"]
    return caption, img_url


async def update_checker(context: CallbackContext):
    scraper: VastgoedScraper
    for scraper in scrapers:
        immmo_name = scraper.get_scraper_name()
        current_listings = scraper.get_current_listings(context)
        new_listings = scraper.store_and_return_new_listings(current_listings)
        print(len(new_listings), "new listings")
        for new_listing in new_listings:
            listing_caption, listing_photo_url = generate_saved_listing_response(
                immmo_name, new_listing
            )

            try:
                await context.bot.send_photo(
                    chat_id=config.OWN_CHAT_ID,
                    photo=listing_photo_url,
                    caption="*NIEUW*\n" + listing_caption,
                    parse_mode="Markdown",
                )
            except BadRequest as e:
                await context.bot.send_message(
                    chat_id=config.OWN_CHAT_ID,
                    text="*NIEUW*\n" + listing_caption,
                    parse_mode="Markdown",
                )


def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    conv_handler = conversation_handler(update_checker)
    application.add_handler(conv_handler)

    application.job_queue.run_repeating(update_checker, interval=config.UPDATE_PERIOD)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
