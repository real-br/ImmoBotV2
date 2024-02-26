# setting path
import sys

sys.path.append("../ImmoBotV2")
from scrapers.VastgoedScraper import VastgoedScraper
import requests
import sqlite3
from sqlite import get_saved_listings, get_listing_data


class LatourEtPetitScraper(VastgoedScraper):

    def get_current_listings(user_id):

        search_data = get_listing_data(
            db_name="databases/user_data.sqlite",
            table_name="user_data",
            user_id=user_id,
        )

        attribute_mapping = {"RENT": "rentals", "BUY": "sales"}

        breakpoint()
        payload = {
            "filters": {"zipcodes": search_data.get("location").split(",")},
            "pagination": {"page": 1, "limit": 100},
            "max_price": search_data.get("budget"),
            "locale": "en",
        }

        headers = {
            "authority": "latouretpetit.be",
        }
        cookies = {
            "CookieConsent": "{stamp:%27G/Yt2FJskuEinCo2xdZr02SkIrNST6rQhmy9lLuEKoFeMQmes0osmg==%27%2Cnecessary:true%2Cpreferences:false%2Cstatistics:false%2Cmarketing:false%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1708948383304%2Cregion:%27be%27}",
        }

        response = requests.post(
            "https://latouretpetit.be/api/estates/{}".format(
                attribute_mapping.get(search_data.get("search_type"))
            ),
            headers=headers,
            json=payload,
            cookies=cookies,
        ).json()

        return response["estates"]

    def store_and_return_new_listings(listings, user_id):

        search_data = get_listing_data(
            db_name="databases/user_data.sqlite",
            table_name="user_data",
            user_id=user_id,
        )

        con = sqlite3.connect("databases/latouretpetit.sqlite")
        cur = con.cursor()
        saved_listing_ids = get_saved_listings(
            "databases/latouretpetit.sqlite", "latouretpetit", user_id
        )

        new_ids = []
        for listing in listings:
            if (
                (listing.get("id") not in saved_listing_ids)
                & (listing.get("rooms") is not None)
                & (listing.get("price") <= search_data.get("budget"))
            ):
                if listing.get("rooms") >= search_data.get("nr_rooms"):
                    id = listing.get("id", None)
                    id_hash = listing.get("_id", None)
                    category = listing.get("preset", None)
                    address = listing.get("address", None)
                    zip = listing.get("zip", None)
                    city = listing.get("city", None)
                    price = listing.get("price", None)
                    epc = listing.get("epc", None)
                    picture_url = listing.get("pictures", [])[0].get("urlSmall", None)
                    listing_url = "https://latouretpetit.be" + listing.get("url", None)
                    nr_rooms = listing.get("rooms", None)
                    listing_type = listing.get("preset", None)

                    cur.execute(
                        "INSERT INTO latouretpetit VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            id,
                            id_hash,
                            category,
                            address,
                            zip,
                            city,
                            price,
                            epc,
                            picture_url,
                            listing_url,
                            nr_rooms,
                            listing_type,
                            user_id,
                        ),
                    )

                    new_ids.append(id)

        con.commit()
        con.close()

        return new_ids

    def get_scraper_name():
        return "LatourEtPetit Properties"

    def get_db_name():
        return "databases/latouretpetit.sqlite"

    def get_listing_table_name():
        return "latouretpetit"


if __name__ == "__main__":
    ls = LatourEtPetitScraper.get_current_listings(6612715685)
    LatourEtPetitScraper.store_and_return_new_listings(ls, 6612715685)
