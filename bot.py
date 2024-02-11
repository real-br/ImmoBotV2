#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=W0613, C0116
# type: ignore[union-attr]
# This program is dedicated to the public domain under the CC0 license.


# https://github.com/python-telegram-bot/python-telegram-bot/


import logging
from scrapers.VastgoedScraper import VastgoedScraper
from scrapers.Century21Scraper import Century21Scraper

# from EraScraper import EraScraper -> no longer working

from scrapers.LecobelScraper import LecobelScraper
from scrapers.JamScraper import JamScraper

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

scrapers = [JamScraper]

STATES_VASTGOED = 0


def generate_saved_listing_response(immo_name, listing):
    price = listing["price"]
    price = f"€{price}" if price is not None else "-"
    caption = f"🌐 [{immo_name.capitalize()}]({listing['url']})\n🏠 {listing['address']}\n💰 {price}"
    img_url = listing["img_url"]
    return caption, img_url


def generate_saved_listing_response_from_db(immo_name, listing):

    listing_info = get_listing_info_for_message(listing, "databases/jam.sqlite", "jam")

    price = listing_info["price"]
    price = f"€{price}" if price is not None else "-"
    caption = f"🌐 [{immo_name.capitalize()}]({listing_info['listing_url']})\n🏠 {listing_info['address']}\n💰 {price}"
    img_url = listing_info["picture_url"]
    return caption, img_url


async def update_checker(application: Application, user_ids: list):
    scraper: VastgoedScraper
    for scraper in scrapers:
        for user_id in user_ids:
            immmo_name = scraper.get_scraper_name()
            current_listings = scraper.get_current_listings(user_id)
            new_listings = scraper.store_and_return_new_listings(
                current_listings, user_id
            )
            try:
                print(len(new_listings), "new listings")
                for new_listing in new_listings:
                    if scraper.get_scraper_name() == "JAM Properties":
                        listing_caption, listing_photo_url = (
                            generate_saved_listing_response_from_db(
                                immmo_name, new_listing
                            )
                        )

                    else:
                        listing_caption, listing_photo_url = (
                            generate_saved_listing_response(immmo_name, new_listing)
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

    conv_handler = conversation_handler(
        asyncio.ensure_future(update_checker(application, user_ids))
    )

    application.add_handler(conv_handler)

    application.job_queue.run_repeating(
        lambda _: asyncio.ensure_future(update_checker(application, user_ids)),
        interval=config.UPDATE_PERIOD,
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
