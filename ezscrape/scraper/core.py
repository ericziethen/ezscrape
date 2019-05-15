#!/usr/bin/env python3

import enum
import logging

import scraper

from typing import Iterator, Optional, Type

import scraper.exceptions as exceptions

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

DEFAULT_REQUEST_TIMEOUT = 5.0
DEFAULT_NEXT_PAGE_TIMEOUT = 3
DEFAULT_JAVASCRIPT_WAIT = 3.0
DEFAULT_MAX_PAGES = 15


@enum.unique
class ScrapeStatus(enum.Enum):
    """Enum for the Download Status."""
    # pylint: disable=invalid-name
    TIMEOUT = 'Timeout'
    SUCCESS = 'Success'
    ERROR = 'Error'


class ScrapeConfig():
    """Class to hold scrape config data needed for downloading the html."""

    def __init__(self, url: str):
        """Initialize a default scrape config with the given url."""
        self.url = url
        self.request_timeout = DEFAULT_REQUEST_TIMEOUT
        self.proxy_server = None
        self.javascript = False
        self.javascript_wait = DEFAULT_JAVASCRIPT_WAIT
        self.useragent = None
        self.attempt_multi_page = False  # TODO - Verify in the end if we even need this field or we can always do it without
        self.next_page_button_xpath = None
        self.max_pages = DEFAULT_MAX_PAGES
        self.next_page_timeout = DEFAULT_NEXT_PAGE_TIMEOUT

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, new_url: str):
        if (not new_url) or (not isinstance(new_url, str)):
            raise exceptions.ScrapeConfigError('Url cannot be blank')
        self._url = new_url


class ScrapePage():
    """Class to represent a single scraped page."""

    def __init__(self, html: str):
        """Initialize the scrape page data."""
        self.html = html
        self.request_time_ms: Optional[float] = None
        self.success = False


class ScrapeResult():
    """Class to keep the Download Result Data."""
    
    def __init__(self, url: str):
        """Initialize the Scrape Result."""
        self._scrape_pages = []
        self._idx = 0

        self.url = url
        # TODO - Move Success to ScrapePage
        self.error_msg = None

    @property
    def request_time_ms(self):
        req_time = 0
        for page in self:
            req_time += page.request_time_ms
        return req_time

    def add_scrape_page(self, html: str, *,
                        scrape_time: Optional[float] = None,
                        success: bool = False):
        """Add a scraped page."""
        page = ScrapePage(html)
        page.request_time_ms = scrape_time
        page.success = success
        self._scrape_pages.append(page)

    def __iter__(self) -> Iterator[ScrapePage]:
        self._idx = 0
        return self

    def __next__(self) -> Type[ScrapePage]:
        try:
            item = self._scrape_pages[self._idx]
        except IndexError:
            raise StopIteration()
        self._idx += 1
        return item

    def __len__(self) -> int:
        return len(self._scrape_pages)

    def __bool__(self) -> bool:
        return bool(self._scrape_pages)


class Scraper():
    """Base Class for Scraper Functionality."""

    def __init__(self, config: ScrapeConfig):
        """Initialize the Scrape Class."""
        self._config = config

    def scrape(self) -> Type[ScrapeResult]:
        """Base function for scraping the config."""
        raise NotImplementedError

    def _validate_config(self) -> bool:
        """Validation function for the config."""
        return True

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, new_config: ScrapeConfig) -> None:
        if not new_config:
            raise ValueError("Config must be provided")
        self._validate_config()
