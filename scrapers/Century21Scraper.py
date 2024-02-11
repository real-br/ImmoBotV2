from scrapers.VastgoedScraper import VastgoedScraper

import base64
import requests
import json
import os
from datetime import datetime

from telegram.ext import (
    CallbackContext,
)


class Century21Scraper(VastgoedScraper):
    def get_current_listings(context: CallbackContext):
        attribute_mapping = {
            "RENT": "FOR_RENT",
        }
        # requirements = base64.b64encode(b'{"bool":{"filter":{"bool":{"must":[{"match":{"agencyId.keyword":"NlqBaHQBXt-nJTnOYaWu"}},{"match":{"listingType":"FOR_RENT"}},{"range":{"rooms.numberOfBedrooms":{"gte":3}}},{"bool":{"should":{"match":{"type":"APARTMENT"}}}},{"range":{"creationDate":{"lte":"2022-09-27T19:40:14.886Z"}}}]}}}}').decode('utf-8')
        requirements = base64.b64encode(
            '{{"bool":{{"filter":{{"bool":{{"must":[{{"bool":{{"should":[{{"match":{{"address.postalCode":"{location}"}}}}]}}}},{{"match":{{"listingType":"{search_type}"}}}},{{"range":{{"rooms.numberOfBedrooms":{{"gte":"{nr_rooms}"}}}}}}]}}}}}}}}'.format(
                location=context.user_data.get("location"),
                search_type=attribute_mapping.get(context.user_data.get("search_type")),
                nr_rooms=context.user_data.get("nr_rooms"),
            ).encode(
                "utf-8"
            )
        ).decode("utf-8")

        # requirements = 'eyJib29sIjp7ImZpbHRlciI6eyJib29sIjp7Im11c3QiOlt7Im1hdGNoIjp7ImFnZW5jeUlkLmtleXdvcmQiOiJObHFCYUhRQlh0LW5KVG5PWWFXdSJ9fSx7Im1hdGNoIjp7Imxpc3RpbmdUeXBlIjoiRk9SX1JFTlQifX0seyJyYW5nZSI6eyJyb29tcy5udW1iZXJPZkJlZHJvb21zIjp7Imd0ZSI6M319fSx7ImJvb2wiOnsic2hvdWxkIjp7Im1hdGNoIjp7InR5cGUiOiJBUEFSVE1FTlQifX19fSx7InJhbmdlIjp7ImNyZWF0aW9uRGF0ZSI6eyJsdGUiOiIyMDIyLTA5LTI3VDE5OjQwOjE0Ljg4NloifX19XX19fX0='
        url = f"https://api.prd.cloud.century21.be/api/v2/properties?facets=elevator,condition,floorNumber,garden,habitableSurfaceArea,listingType,numberOfBedrooms,parking,price,subType,surfaceAreaGarden,swimmingPool,terrace,totalSurfaceArea,type&filter={requirements}&pageSize=36&sort=-creationDate"
        response = requests.get(url).json()
        # return "\n".join([Century21Scraper.get_url(l) for l in response['data']])
        # print("\n".join([Century21Scraper.get_listing_img_url(l) for l in response['data']]))

        return response["data"]

    def get_saved_listings():
        with open(Century21Scraper.get_datapath(), "r") as file:
            saved_listings = json.load(file)
        return saved_listings

    def get_url(listing):
        return f"https://www.century21.be/nl/pand/te-huur/appartement/{listing['address']['city'].lower()}/{listing['id']}"

    def get_listing_img_url(listing):
        img_url_str = (
            '{"key":"property-assets/'
            + listing["id"]
            + "/"
            + listing["images"][0]["name"]
            + '","edits":{"jpeg":{"quality":100},"rotate":null,"resize":{"withoutEnlargement":true,"width":284}}}'
        )
        return f'https://images.century21.be/{base64.b64encode(img_url_str.encode("utf-8")).decode("utf-8")}'

    def store_and_return_new_listings(listings):
        def _convert_to_saved_listing_format(listing):
            # fields: id, price, address, url, img_url, datetime_added
            formatted = dict()
            formatted["id"] = listing["id"]
            formatted["price"] = listing["price"]["amount"]
            formatted["address"] = (
                listing["address"]["street"]
                + " "
                + listing["address"]["number"]
                + ", "
                + listing["address"]["city"]
            )
            formatted["url"] = Century21Scraper.get_url(listing)
            formatted["img_url"] = Century21Scraper.get_listing_img_url(listing)
            now = datetime.now()
            formatted["datetime_added"] = now.strftime("%d/%m/%Y %H:%M:%S")

            return formatted

        with open(Century21Scraper.get_datapath(), "r") as file:
            saved_listings = json.load(file)
        ids_saved_listings = set([listing["id"] for listing in saved_listings])

        listings_formatted = [
            _convert_to_saved_listing_format(listing) for listing in listings
        ]
        new_listings = []
        for listing in listings_formatted:
            if listing["id"] in ids_saved_listings:
                continue

            new_listings.append(listing)

        if len(new_listings) > 0:
            with open(Century21Scraper.get_datapath(), "w") as file:
                json.dump(new_listings + saved_listings, file)

        return new_listings

    def get_scraper_name():
        return "Century21"

    def get_datapath():
        return os.path.join("century21.json")


# Init directory upon import
if not os.path.exists(Century21Scraper.get_datapath()):
    with open(Century21Scraper.get_datapath(), "w") as f:
        f.write("[]")

if __name__ == "__main__":
    ls = Century21Scraper.get_current_listings()
    Century21Scraper.store_and_return_new_listings(ls)
