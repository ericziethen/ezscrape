#!/usr/bin/env python3

"""Module providing core definitions for scraper functionality."""

import enum
import logging

from dataclasses import dataclass
from typing import Iterator, List, Optional

import ezscrape.scraping.exceptions as exceptions

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

DEFAULT_REQUEST_TIMEOUT = 5.0
DEFAULT_MAX_PAGES = 15


@enum.unique
class ScrapeStatus(enum.Enum):
    """Enum for the Download Status."""

    # pylint: disable=invalid-name
    UNKNOWN = 'Unknown'
    TIMEOUT = 'Timeout'
    SUCCESS = 'Success'
    ERROR = 'Error'
    PROXY_ERROR = 'Proxy Error'


@enum.unique
class WaitForPageType(enum.Enum):
    """Enum for Wait for page types."""

    # pylint: disable=invalid-name
    XPATH = 'xpath'


class WaitForPageElem():
    """Class to define how to wait for a page."""

    def __init__(self, wait_type: WaitForPageType, wait_text: str):
        """Set up the Wait Element."""
        self.wait_text = wait_text
        self.wait_type = wait_type

    @property
    def wait_text(self) -> str:
        """Property to define the wait_text attribute."""
        return self._wait_text

    @wait_text.setter
    def wait_text(self, new_wait_text: str) -> None:
        """Setter for the wait_text attribute."""
        if not isinstance(new_wait_text, str):
            raise ValueError('wait_text need to be a valid str')
        # pylint: disable=attribute-defined-outside-init
        self._wait_text = new_wait_text
        # pylint: enable=attribute-defined-outside-init

    @property
    def wait_type(self) -> WaitForPageType:
        """Property to define the wait_type attribute."""
        return self._wait_type

    @wait_type.setter
    def wait_type(self, new_wait_type: WaitForPageType) -> None:
        """Setter for the wait_type attribute."""
        if not isinstance(new_wait_type, WaitForPageType):
            raise ValueError('wait_type need to be a valid str')
        # pylint: disable=attribute-defined-outside-init
        self._wait_type = new_wait_type
        # pylint: enable=attribute-defined-outside-init


class WaitForXpathElem(WaitForPageElem):
    """A wait for Xpath Element."""

    def __init__(self, xpath: str):
        """Set up the Xpath Element."""
        super().__init__(WaitForPageType.XPATH, xpath)


class ScrapeConfig():
    """Class to hold scrape config data needed for downloading the html."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, url: str):
        """Initialize a default scrape config with the given url."""
        self.url = url

        self.request_timeout = DEFAULT_REQUEST_TIMEOUT
        self.page_load_wait = 0

        self.proxy_http = ''
        self.proxy_https = ''
        self.useragent = None
        self.max_pages = DEFAULT_MAX_PAGES

        self.next_button: Optional[WaitForPageElem] = None
        self.wait_for_elem_list: List[WaitForPageElem] = []

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


@dataclass
class ScrapePage():
    """Class to represent a single scraped page."""

    html: str
    request_time_ms: float = 0
    status = ScrapeStatus.UNKNOWN


class ScrapeResult():
    """Class to keep the Download Result Data."""

    def __init__(self, url: str):
        """Initialize the Scrape Result."""
        self._scrape_pages: List[ScrapePage] = []
        self._idx = 0

        self.url = url
        self.caller_ip = None
        self.status: ScrapeStatus = ScrapeStatus.UNKNOWN
        self.error_msg = ''

    @property
    def request_time_ms(self) -> float:
        """Property to calculate the combined request time."""
        req_time = 0.0
        for page in self:
            req_time += page.request_time_ms
        return req_time

    @property
    def first_page(self) -> Optional[ScrapePage]:
        """Property to get the first page scraped."""
        if self._scrape_pages:
            return self._scrape_pages[0]

        return None

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
