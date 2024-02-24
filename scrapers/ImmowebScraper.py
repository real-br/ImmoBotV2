from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import sqlite3
import sys
import re
import config


sys.path.append("../ImmoBotV2")
from sqlite import get_saved_listings, get_listing_data
from scrapers.VastgoedScraper import VastgoedScraper


class ImmowebScraper(VastgoedScraper):

    def initialize_driver(self) -> webdriver.Firefox:
        options = FirefoxOptions()
        options.add_argument("--headless")
        return webdriver.Firefox(options=options)

    def get_souped_html(self, driver: webdriver.Firefox, url: str) -> BeautifulSoup:

        driver.get(url)
        html = driver.page_source
        return BeautifulSoup(html, "html.parser")

    def get_current_listings(self):

        listing_types = ["te-huur", "te-koop"]
        attribute_mapping = {"te-huur": "RENT", "te-koop": "BUY"}

        driver = self.initialize_driver()

        listings_info = []
        for listing_type in listing_types:
            page_number = 1
            while page_number <= config.PAGES_SCRAPED:
                print("Page {} / {}".format(page_number, config.PAGES_SCRAPED))
                main_url = "https://www.immoweb.be/nl/zoeken/huis-en-appartement/{}?countries=BE&page={}&orderBy=newest"
                soup = self.get_souped_html(
                    driver,
                    main_url.format(
                        listing_type,
                        page_number,
                    ),
                )
                iw_search_elements = soup.find_all("li", "search-results__item")
                for html_content in iw_search_elements:

                    article = html_content.select_one("article")

                    listing_id = ""
                    if article:
                        article_id = article["id"]
                        listing_id = (
                            int("".join(filter(str.isdigit, article_id)))
                            if article_id
                            else None
                        )

                    else:
                        continue

                    url = html_content.find("a").get("href")

                    card_media_background = html_content.select_one(
                        ".card__media-background"
                    )
                    background_image = (
                        card_media_background["style"]
                        .split('("', 1)[-1]
                        .split('")', 1)[0]
                        if card_media_background
                        else None
                    )

                    card_price = html_content.select_one(
                        '.card--result__price span[aria-hidden="true"]'
                    )

                    price_text = (
                        card_price.get_text(strip=True).replace("\xa0", "")
                        if card_price
                        else None
                    ).replace(".", "")
                    price = int(re.search(r"\d+", price_text).group())

                    locality_info = html_content.select_one(
                        ".card__information--locality"
                    )
                    locality_text = (
                        locality_info.get_text(strip=True) if locality_info else None
                    )
                    zipcode, city = (
                        locality_text.split(" ", 1) if locality_text else None
                    )

                    card_description = html_content.select_one(".card__description")
                    description_text = (
                        card_description.get_text(strip=True)
                        if card_description
                        else None
                    )

                    nr_rooms = html_content.select_one(".card__information--property")
                    nr_rooms_text = nr_rooms.get_text(strip=True) if nr_rooms else None
                    nr_rooms_int = (
                        int(nr_rooms_text.split(" ", 1)[0])
                        if (
                            (len(nr_rooms_text.split(" ", 1)[0]) > 0)
                            & (len(nr_rooms_text.split(" ", 1)[0]) <= 2)
                        )
                        else -1
                    )

                    listing_info = {
                        "id": listing_id,
                        "id_hash": str(hash(listing_id)),
                        "category": None,
                        "address": description_text,
                        "zip": zipcode,
                        "city": city,
                        "price": price,
                        "epc": None,
                        "picture_url": background_image,
                        "listing_url": url,
                        "nr_rooms": nr_rooms_int,
                        "listing_type": attribute_mapping.get(listing_type),
                    }
                    # Add the dictionary to the list of listings information
                    listings_info.append(listing_info)

                page_number += 1

        driver.quit()
        return listings_info

    def store_and_return_new_listings(self, listings, user_id):

        search_data = get_listing_data(
            db_name="databases/user_data.sqlite",
            table_name="user_data",
            user_id=user_id,
        )

        con = sqlite3.connect(self.get_db_name())
        cur = con.cursor()

        saved_listing_ids = get_saved_listings(
            self.get_db_name(), self.get_listing_table_name(), user_id
        )

        new_ids = []
        for listing in listings:
            if (
                (listing.get("id") not in saved_listing_ids)
                & (listing.get("zip") in search_data.get("location"))
                & (listing.get("price") <= search_data.get("budget"))
                & (
                    (listing.get("nr_rooms") == -1)
                    | (listing.get("nr_rooms") >= search_data.get("nr_rooms"))
                )
                & (listing.get("listing_type") == search_data.get("search_type"))
            ):
                id = listing.get("id", None)
                id_hash = listing.get("id_hash", None)
                category = listing.get("category", None)
                address = listing.get("address", None)
                zip = listing.get("zip", None)
                city = listing.get("city", None)
                price = listing.get("price", None)
                epc = listing.get("epc", None)
                picture_url = listing.get("picture_url", None)
                listing_url = listing.get("listing_url", None)
                nr_rooms = listing.get("nr_rooms", None)
                listing_type = listing.get("listing_type", None)

                cur.execute(
                    "INSERT INTO immoweb VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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

    def get_scraper_name(self):
        return "Immoweb"

    def get_db_name(self):
        return "databases/immoweb.sqlite"

    def get_listing_table_name(self):
        return "immoweb"


if __name__ == "__main__":
    immoweb_scraper = ImmowebScraper()
    ls = immoweb_scraper.get_current_listings()
    immoweb_scraper.store_and_return_new_listings(ls, 6612715685)
