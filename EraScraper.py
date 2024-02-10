from VastgoedScraper import VastgoedScraper
import config

from bs4 import BeautifulSoup
import requests
import regex as re
import json
from datetime import datetime
import os

from telegram.ext import (
    CallbackContext,
)


class EraScraper(VastgoedScraper):

    def get_current_listings(context: CallbackContext):

        attribute_mapping = {
            "FOR_RENT": "te-huur",
            "1060": "2884",
            "1050": "2877",
        }

        url = "https://www.era.be/nl/{search_type}?filter%5Blocation%5D%5Bsub_municipalities%5D={postalcode}&filter%5Bprice%5D=%28min%3A1%3Bmax%3A{budget}%29&filter%5Bamount_bedrooms%5D=%28min%3A{nr_rooms}%3Bmax%3A%29".format(
            search_type=attribute_mapping.get(context.user_data.get("search_type")),
            postalcode=attribute_mapping.get(context.user_data.get("location")),
            budget=context.user_data.get("budget"),
            nr_rooms=context.user_data.get("nr_rooms"),
        )

        breakpoint()

        html = requests.get(
            "https://www.era.be/nl/{search_type}?filter%5Blocation%5D%5Bsub_municipalities%5D={postalcode}&filter%5Bprice%5D=%28min%3A1%3Bmax%3A{budget}%29&filter%5Bamount_bedrooms%5D=%28min%3A{nr_rooms}%3Bmax%3A%29".format(
                search_type=attribute_mapping.get(context.user_data.get("search_type")),
                postalcode=attribute_mapping.get(context.user_data.get("location")),
                budget=context.user_data.get("budget"),
                nr_rooms=context.user_data.get("nr_rooms"),
            )
        ).text
        soup = BeautifulSoup(html, "html.parser")
        property_divs = soup.find_all("div", class_="property-teaser__content")

        breakpoint()

        listings = []

        for property in property_divs:
            property_state_div = property.find("div", class_="property-state")
            breakpoint()
            if property_state_div is not None:
                property_state = property_state_div.get("class")  # list
                if "sold" in property_state or "in-option" in property_state:
                    continue

            listing = dict()
            listing["id"] = property.find("div", class_="property-id-holder").get(
                "data-property-id"
            )
            listing["address"] = property.find(
                "div", class_="field-name-era-adres--c"
            ).text.strip()
            listing["url"] = "https://www.era.be" + property.find(
                "div", class_="field-item"
            ).find("a").get("href")
            try:
                listing["price"] = int(
                    re.findall(
                        r"([\d]+)",
                        property.find("div", class_="total-rent-price")
                        .text.replace(" ", "")
                        .replace(".", "")
                        .strip(),
                    )[0]
                )
            except:
                listing["price"] = None
            listing["img_url"] = property.find("img").get("src")
            now = datetime.now()
            listing["datetime_added"] = now.strftime("%d/%m/%Y %H:%M:%S")
            listings.append(listing)
            breakpoint()

        return listings

    def store_and_return_new_listings(listings):
        with open(EraScraper.get_datapath(), "r") as file:
            saved_listings = json.load(file)
        ids_saved_listings = set([listing["id"] for listing in saved_listings])

        new_listings = []
        for listing in listings:
            if listing["id"] in ids_saved_listings:
                continue

            new_listings.append(listing)

        if len(new_listings) > 0:
            with open(EraScraper.get_datapath(), "w") as file:
                json.dump(new_listings + saved_listings, file)

        return new_listings

    def get_saved_listings():
        with open(EraScraper.get_datapath(), "r") as file:
            saved_listings = json.load(file)
        return saved_listings

    def get_scraper_name():
        return "Era Chatelain"

    def get_datapath():
        return os.path.join("era.json")


# Init directory upon import
if not os.path.exists(EraScraper.get_datapath()):
    with open(EraScraper.get_datapath(), "w") as f:
        f.write("[]")

if __name__ == "__main__":
    ls = EraScraper.get_current_listings()
    print(ls)
    EraScraper.store_and_return_new_listings(ls)
