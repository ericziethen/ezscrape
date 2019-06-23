#!/usr/bin/env python3

"""Module providing core definitions for scraper functionality."""

import enum
import logging

from typing import Iterator, List

import scraping.exceptions as exceptions

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

DEFAULT_REQUEST_TIMEOUT = 5.0
DEFAULT_MAX_PAGES = 15  # TODO - Maybe this should be 2 and if needed more need to be explicit


@enum.unique
class ScrapeStatus(enum.Enum):
    """Enum for the Download Status."""

    # pylint: disable=invalid-name
    UNKNOWN = 'Unknown'
    TIMEOUT = 'Timeout'
    SUCCESS = 'Success'
    ERROR = 'Error'
    PROXY_ERROR = 'Proxy Error'


class ScrapeConfig():
    """Class to hold scrape config data needed for downloading the html."""

    def __init__(self, url: str):
        """Initialize a default scrape config with the given url."""
        # TODO - FOr Simplification, maybe pass some arguments through init with defaults
        # TODO - and have functions for others like proxy, useragent...
        # TODO - otherwise document each and purpose
        self.url = url
        self.request_timeout = DEFAULT_REQUEST_TIMEOUT
        self.proxy_http = ''
        self.proxy_https = ''
        self.useragent = None
        self.max_pages = DEFAULT_MAX_PAGES
        # TODO - Think if we have some sort of sub structure, or type for next button e.g. xpath to stay flexible in the future
        self.xpath_next_button = ''
        self.xpath_wait_for_loaded = ''
        self.wait_for_page_load_seconds = 0

    @property
    def url(self) -> str:
        """Property to define the Url attribute."""
        return self._url

    @url.setter
    def url(self, new_url: str) -> None:
        """Setter for the Url attribute."""
        if (not new_url) or (not isinstance(new_url, str)):
            raise exceptions.ScrapeConfigError('Url cannot be blank')
        self._url = new_url  # pylint: disable=attribute-defined-outside-init

    def __str__(self) -> str:
        return str(self.__dict__)


class ScrapePage():
    """Class to represent a single scraped page."""

    def __init__(self, html: str):
        """Initialize the scrape page data."""
        self.html = html
        self.request_time_ms: float = 0
        self.status = ScrapeStatus.UNKNOWN


class ScrapeResult():
    """Class to keep the Download Result Data."""

    def __init__(self, url: str):
        """Initialize the Scrape Result."""
        self._scrape_pages: List[ScrapePage] = []
        self._idx = 0

        self.url = url
        self.caller_ip = None

        # TODO - Status should be (_scrape_pages > 0) and (not error_msg)
        # TODO - Or some other logic
        self.status: ScrapeStatus = ScrapeStatus.UNKNOWN
        self.error_msg = ''

    @property
    def request_time_ms(self) -> float:
        """Property to calculate the combined request time."""
        req_time = 0.0
        for page in self:
            req_time += page.request_time_ms
        return req_time

    def add_scrape_page(self, html: str, *,
                        scrape_time: float = 0,
                        status: ScrapeStatus) -> None:
        """Add a scraped page."""
        page = ScrapePage(html)
        page.request_time_ms = scrape_time
        page.status = status
        self._scrape_pages.append(page)

    def __iter__(self) -> Iterator[ScrapePage]:
        self._idx = 0
        return self

    def __next__(self) -> ScrapePage:
        try:
            item = self._scrape_pages[self._idx]
        except IndexError:
            raise StopIteration()
        self._idx += 1
        return item

    def __len__(self) -> int:
        return len(self._scrape_pages)

    def __bool__(self) -> bool:
        return self.status == ScrapeStatus.SUCCESS


class Scraper():
    """Base Class for Scraper Functionality."""

    def __init__(self, config: ScrapeConfig):
        """Initialize the Scrape Class."""
        print(F'Scraper.__init__()')
        self.config: ScrapeConfig = config

    @classmethod
    def _validate_config(cls, config: ScrapeConfig) -> None:
        """Validate the Scrapers config."""
        if config is None:
            raise ValueError("Config must be provided")

    @property
    def config(self) -> ScrapeConfig:
        """Property to define the config parameter."""
        return self._config

    @config.setter
    def config(self, new_config: ScrapeConfig) -> None:
        print(F'Scraper.@config.setter')
        # Check in setter because True for subclasses as well
        if new_config is None:
            raise ValueError("Config must be provided")

        self._validate_config(new_config)

        # pylint: disable=attribute-defined-outside-init
        self._config = new_config
        # pylint: enable=attribute-defined-outside-init

    def scrape(self) -> ScrapeResult:
        """Scrape based on the set config."""
        raise NotImplementedError

    def __str__(self) -> str:
        return F'{type(self).__name__} for Url: {self.config.url}'
