from abc import ABC, abstractmethod


class VastgoedScraper(ABC):

    @abstractmethod
    def get_current_listings(user_id):
        pass

    @abstractmethod
    def store_and_return_new_listings(listings):
        pass

    @abstractmethod
    def get_saved_listings():
        pass

    @abstractmethod
    def get_scraper_name():
        pass

    @abstractmethod
    def get_datapath():
        pass
