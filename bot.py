import sys

sys.path.append("ImmoBotV2")

import logging
from scrapers.VastgoedScraper import VastgoedScraper
from scrapers.JamScraper import JamScraper
from scrapers.ImmowebScraper import ImmowebScraper
import time
import threading
import asyncio
from datetime import datetime, timedelta


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
from sqlite import get_listing_info_for_message, get_user_ids, get_username


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
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

scrapers = [JamScraper]


def main():
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    user_ids = get_user_ids("databases/user_data.sqlite", "user_data")

    conv_handler = conversation_handler()

    application.add_handler(conv_handler)

    # Start the update_checker in a separate thread
    update_checker_thread = threading.Thread(
        target=update_checker,
        args=(application, user_ids),
        name="update-checker-thread",
    )
    update_checker_thread.start()
    logger.info(f"update_checker scheduled to run every {config.UPDATE_PERIOD} seconds")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


def generate_saved_listing_response_from_db(db_name, table_name, immo_name, listing):

    listing_info = get_listing_info_for_message(listing, db_name, table_name)

    price = listing_info["price"]
    price = f"€{price}" if price is not None else "-"
    caption = f"🌐 [{immo_name.capitalize()}]({listing_info['listing_url']})\n🏠 {listing_info['address']}\n📍 {listing_info['zip']}\n💰 {price}"
    img_url = listing_info["picture_url"]
    return caption, img_url


def update_checker_logic(application: Application, user_ids: list):
    scraper: VastgoedScraper
    for scraper in scrapers:
        logger.info(f"Checking for new listings from {scraper.get_scraper_name()}")
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
                logger.info(f"Found {len(new_listings)} new listings")
                for new_listing in new_listings:
                    listing_caption, listing_photo_url = (
                        generate_saved_listing_response_from_db(
                            db_name, listing_table_name, immmo_name, new_listing
                        )
                    )
                    try:
                        send_listing_photo(
                            application, user_id, listing_photo_url, listing_caption
                        )
                    except Exception as e:
                        logger.error(
                            f"Failed to send listing photo and caption. Error: {str(e)}"
                        )
                        logger.exception(e)
            except Exception as e:
                logger.error(f"Failed to process new listings. Error: {str(e)}")
                logger.exception(e)


def update_checker(application, user_ids):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            update_checker_logic(application, user_ids)
            current_time = datetime.now()
            next_run_time = current_time + timedelta(seconds=config.UPDATE_PERIOD)
            logger.info(
                f"Update checker executed at {current_time}, next run time for update_checker: {next_run_time}"
            )
            time.sleep(config.UPDATE_PERIOD)
    except Exception as e:
        print(f"Error in update_checker: {e}")
    finally:
        loop.close()


async def send_listing_photo(application, user_id, listing_photo_url, listing_caption):
    username = get_username("databases/user_data.sqlite", "user_data", user_id)

    try:
        await application.bot.send_photo(
            chat_id=user_id,
            photo=listing_photo_url,
            caption="*NIEUW*\n" + listing_caption,
            parse_mode="Markdown",
        )
        logger.info(
            "Sent new listing photo and caption to {username} ({user_id})".format(
                username=username, user_id=user_id
            )
        )
    except BadRequest as e:
        await application.bot.send_message(
            chat_id=user_id,
            text="*NIEUW*\n" + listing_caption,
            parse_mode="Markdown",
        )
        logger.info(
            "Sent new listing caption (photo failed) to {username} ({user_id})".format(
                username=username, user_id=user_id
            )
        )


if __name__ == "__main__":
    main()
