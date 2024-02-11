from scrapers.VastgoedScraper import VastgoedScraper
import requests
import sqlite3
from sqlite import get_saved_listings, get_table_data


class JamScraper(VastgoedScraper):

    def get_current_listings(user_id):

        search_data = get_table_data(
            db_name="databases/user_data.sqlite",
            table_name="user_data",
            user_id=user_id,
        )

        attribute_mapping = {"RENT": "FOR_RENT", "BUY": "FOR_SALE"}

        payload = {
            "needImages": 1,
            "langue": "en",
            "purpose": attribute_mapping.get(search_data.get("search_type")),
            "limit": 99999,
            "deleted": 0,
            "price_max": str(search_data.get("budget")),
        }

        headers = {
            "authority": "realty.itcl.io",
            "authorization": "01iOmjBODrZe2Igres-7QlDtF96rf7nbarTMgXkze4A",
            "id": "jam",
        }

        response = requests.post(
            "https://realty.itcl.io/estates", headers=headers, json=payload
        ).json()

        return response["Result"]

    def store_and_return_new_listings(listings, user_id):

        con = sqlite3.connect("databases/jam.sqlite")
        cur = con.cursor()

        saved_listing_ids = get_saved_listings("databases/jam.sqlite", "jam", user_id)

        new_ids = []
        for listing in listings:
            if listing.get("id") not in saved_listing_ids:
                id = listing.get("id", None)
                id_hash = listing.get("_id", None)
                category = listing.get("category", None)
                address = listing.get("address", None)
                zip = listing.get("zip", None)
                city = listing.get("city", None)
                price = listing.get("price", None)
                epc = listing.get("epc", None)
                picture_url = listing.get("pictures", [])[0].get("url", None)
                listing_url = "https://www.jamproperties.be/en/for-sale/{category}/{city}/{id}".format(
                    category=category, city=city, id=id
                )

                cur.execute(
                    "INSERT INTO jam VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
                        user_id,
                    ),
                )

                new_ids.append(id)

        con.commit()
        con.close()

        return new_ids

    def get_scraper_name():
        return "JAM Properties"

    def get_datapath():
        return ""


if __name__ == "__main__":
    ls = JamScraper.get_current_listings()
    JamScraper.store_and_return_new_listings(ls)
