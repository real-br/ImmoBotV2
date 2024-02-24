#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.


# https://github.com/python-telegram-bot/python-telegram-bot/


import sys

sys.path.append("ImmoBotV2")

import logging
from scrapers.VastgoedScraper import VastgoedScraper
from scrapers.JamScraper import JamScraper
from scrapers.ImmowebScraper import ImmowebScraper
import schedule
import time


from interaction import (
    conversation_handler,
)
import config
import glob

from telegram import Update
from telegram.ext import (
    Application,
)
from telegram.error import BadRequest
from sqlite import get_listing_info_for_message, get_user_ids
import asyncio


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


immoweb_instance = ImmowebScraper()

scrapers = [JamScraper, immoweb_instance]

STATES_VASTGOED = 0


def generate_saved_listing_response_from_db(db_name, table_name, immo_name, listing):

    listing_info = get_listing_info_for_message(listing, db_name, table_name)

    price = listing_info["price"]
    price = f"€{price}" if price is not None else "-"
    caption = f"🌐 [{immo_name.capitalize()}]({listing_info['listing_url']})\n🏠 {listing_info['address']}\n📍 {listing_info['zip']}\n💰 {price}"
    img_url = listing_info["picture_url"]
    return caption, img_url


def update_checker(application: Application, user_ids: list):
    scraper: VastgoedScraper
    for scraper in scrapers:

        current_listings_immoweb = {}
        if scraper.get_scraper_name() == "Immoweb":
            current_listings_immoweb = scraper.get_current_listings()

        for user_id in user_ids:
            immmo_name = scraper.get_scraper_name()
            db_name = scraper.get_db_name()
            listing_table_name = scraper.get_listing_table_name()
            current_listings = (
                scraper.get_current_listings(user_id)
                if scraper.get_scraper_name() != "Immoweb"
                else current_listings_immoweb
            )

            new_listings = scraper.store_and_return_new_listings(
                current_listings, user_id
            )
            try:
                print(len(new_listings), "new listings")
                for new_listing in new_listings:
                    listing_caption, listing_photo_url = (
                        generate_saved_listing_response_from_db(
                            db_name, listing_table_name, immmo_name, new_listing
                        )
                    )
                    try:
                        await application.bot.send_photo(
                            chat_id=user_id,
                            photo=listing_photo_url,
                            caption="*NIEUW*\n" + listing_caption,
                            parse_mode="Markdown",
                        )
                    except BadRequest as e:
                        await application.bot.send_message(
                            chat_id=user_id,
                            text="*NIEUW*\n" + listing_caption,
                            parse_mode="Markdown",
                        )
            except Exception as e:
                print(
                    "Failed because there are {}".format(len(new_listings))
                    + " new listings"
                )


def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    user_ids = get_user_ids("databases/user_data.sqlite", "user_data")

    conv_handler = conversation_handler()

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

    schedule.every(config.UPDATE_PERIOD).seconds.do(
        update_checker, application, user_ids
    )


if __name__ == "__main__":
    main()
