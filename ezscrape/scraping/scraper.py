#!/usr/bin/env python3

"""Main Scrape Functionality."""

import ipaddress
import logging
import urllib

from typing import Optional

import ezscrape.scraping.scraper_requests as scraper_requests
import ezscrape.scraping.scraper_selenium as scraper_selenium

import ezscrape.scraping.core as core
import ezscrape.scraping.exceptions as exceptions

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

SPECIAL_LOCAL_ADDRESSES = [
    'localhost',
    '0.0',
    '127.1'
]


def scrape_url(config: core.ScrapeConfig) -> core.ScrapeResult:
    """Handle all scraping requests."""
    scraper: Optional[core.Scraper] = None

    # 1.) Try to use Normal Requests Model
    if scraper is None:
        try:
            scraper = scraper_requests.RequestsScraper(config)
        except exceptions.ScrapeConfigError:
            pass

    # 2.) Try Using Selenium chrome if no scraper found yet
    if scraper is None:
        try:
            scraper = scraper_selenium.SeleniumChromeScraper(config)
        except exceptions.ScrapeConfigError:
            pass

    if scraper is not None:
        result = scraper.scrape()
    else:
        raise ValueError(F'No Scraper found for config: {config}')

    return result


def is_local_address(url: str) -> bool:
    """Check whether the given url is a local address."""
    # Parse the URL
    result = urllib.parse.urlparse(url)
    addr = result.netloc
    if not addr:
        addr = result.path
    addr = addr.split(':')[0].lower()

    # Check if it is a special local address
    if addr in SPECIAL_LOCAL_ADDRESSES:
        return True

    # Check the Ip Range
    is_private = False
    try:
        is_private = ipaddress.ip_address(addr).is_private
    except ValueError:
        is_private = False
    return is_private


def check_url(url: str, *, local_only: bool) -> bool:
    """Check if the Local url is reachable."""
    if local_only and (not is_local_address(url)):
        raise ValueError('Url is not a local address')

    result = scrape_url(core.ScrapeConfig(url))

    return result.status == core.ScrapeStatus.SUCCESS
