from distutils.command.config import config
from VastgoedScraper import VastgoedScraper
from bs4 import BeautifulSoup
import requests
import regex as re
import json
from datetime import datetime
import os
import config

from telegram.ext import (
    CallbackContext,
)


class LecobelScraper(VastgoedScraper):

    def get_current_listings(context: CallbackContext):

        attribute_mapping = {
            "FOR_RENT": "renting",
        }

        html = requests.get(
            "https://www.lecobel-vaneau.be/nl/vaneau-search/search?field_ad_type[eq][]={search_type}&field_bedrooms_number[eq][]={nr_rooms}&field_price[eq][]=price_68&field_price[eq][]=price_69&field_property_type[eq][]=38&limit=28&location[eq][]=zip_{postalcode}&mode=list&offset=0&offset_additional=0&search_page_id=580".format(
                search_type=attribute_mapping.get(context.user_data.get("search_type")),
                nr_rooms=context.user_data.get("nr_rooms"),
                postalcode=context.user_data.get("location"),
            )
        ).text
        html = (
            json.loads(html)["html"].encode("unicode_escape").decode("unicode_escape")
        )
        soup = BeautifulSoup(html, "html.parser")

        see_more_element = soup.find("div", class_="block-items__see-more")
        for e in see_more_element.find_all_next():
            e.clear()
        property_divs = soup.find_all("div", class_="property property__search-item")

        listings = []

        for property in property_divs:
            listing = dict()
            listing["id"] = property.get("data-node-id")
            listing["address"] = (
                property.find("div", class_="property-name")
                .text.replace(" ", "")
                .replace("\n", "")
                .strip()
            )
            listing["url"] = (
                "https://www.lecobel-vaneau.be" + property.find("a").get("href").strip()
            )
            try:
                listing["price"] = int(
                    re.findall(
                        r"([\d]+)",
                        property.find("div", class_="property-price")
                        .text.replace(" ", "")
                        .replace(".", "")
                        .strip(),
                    )[0]
                )
            except:
                listing["price"] = None
            listing["img_url"] = (
                "https://www.lecobel-vaneau.be"
                + property.find("source").get("srcset").strip()
            )
            now = datetime.now()
            listing["datetime_added"] = now.strftime("%d/%m/%Y %H:%M:%S")
            listings.append(listing)

        return listings

    def store_and_return_new_listings(listings):
        with open(LecobelScraper.get_datapath(), "r") as file:
            saved_listings = json.load(file)
        ids_saved_listings = set([listing["id"] for listing in saved_listings])

        new_listings = []
        for listing in listings:
            if listing["id"] in ids_saved_listings:
                continue

            new_listings.append(listing)

        if len(new_listings) > 0:
            with open(LecobelScraper.get_datapath(), "w") as file:
                json.dump(new_listings + saved_listings, file)

        return new_listings

    def get_saved_listings():
        with open(LecobelScraper.get_datapath(), "r") as file:
            saved_listings = json.load(file)
        return saved_listings

    def get_scraper_name():
        return "Lecobel Vaneau"

    def get_datapath():
        return os.path.join("lecobel.json")


# Init directory upon import
if not os.path.exists(LecobelScraper.get_datapath()):
    with open(LecobelScraper.get_datapath(), "w") as f:
        f.write("[]")


if __name__ == "__main__":
    ls = LecobelScraper.get_current_listings()
    LecobelScraper.store_and_return_new_listings(ls)
