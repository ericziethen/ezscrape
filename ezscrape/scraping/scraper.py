#!/usr/bin/env python3

"""Main Scrape Functionality."""

import ipaddress
import logging

import scraping.scraper_requests
import scraping.scraper_requests_html
import scraping.scraper_selenium


import scraping.core as core

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

SPECIAL_LOCAL_ADDRESSES = [
    'localhost',
    '0.0',
    '127.1'
]


def scrape_url(config: core.ScrapeConfig) -> core.ScrapeResult:
    """Generic function to handle all scraping requests."""
    raise NotImplementedError


def is_local_address(url: str) -> bool:
    """Simple check whether the given url is a local address."""
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

    config = core.ScrapeConfig(url)
    result = scraping.scraper_requests.scrape_url_requests(config)

    # TODO - There mist be a better way if the request succeeded than 
    # TODO - accessing the underlying data directly
    # TODO - Maybe need a derived value
    # TODO - Maybe can use an Enum Value to represent different success states
    if result and (result._scrape_pages[0].success):
        return True
    else:
        return False
