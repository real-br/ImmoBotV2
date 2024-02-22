from abc import ABC, abstractmethod


class VastgoedScraper(ABC):

    @abstractmethod
    def get_current_listings(user_id):
        pass

    @abstractmethod
    def store_and_return_new_listings(listings):
        pass

    @abstractmethod
    def get_scraper_name():
        pass

    @abstractmethod
    def get_db_name(self):
        pass

    @abstractmethod
    def get_listing_table_name(self):
        pass
