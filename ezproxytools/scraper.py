#!/usr/bin/env python3

"""Provide Website downloading functionality."""

import ipaddress
import os
import requests_html
import urllib.error
import urllib.parse
import urllib.request

from typing import Optional

SPECIAL_LOCAL_ADDRESSES = [
    'localhost',
    '0.0',
    '127.1'
]

class PageDownloadError(Exception):
    """Generic Page Download Error."""


class IncompletePagesError(PageDownloadError):
    """Exception when failed to download all pages."""


class Result():
    """Class to keep the Download Result Data."""

    def __init__(self, response):
        """Initialize the Scrape Result."""
        self._response = response
        self.html_pages = []

        for html in response.html:
            self.html_pages.append(html.html)
            print(F'ERIC:::"{html.html}"')

    @property
    def result_good(self) -> bool:
        """Check if the result is ok,"""
        return self._response.status_code == 200

'''
!!! If I cannot find a way to not download CHromium automatically, maybe easier
!!! to use headless chromium and then we don't need html-requests but onlye requests
!!! but it might be ok for us to do as well, esecially when using Internally and in an
!!! automated way it should only download once
'''

def scrape_url(url: str, *, proxy_url: Optional[str] = None,
               load_javascript: bool = False) -> Result:
    """Download the given url with the given proxy if specified."""

    session = requests_html.HTMLSession()
    response = session.get(url)
    if load_javascript:
        response.html.render()
    result = Result(response)

    return result


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

    try:
        with urllib.request.urlopen(url) as result:
            code = result.getcode()
        if code == 200:
            return True
    except urllib.error.URLError:
        return False
    return False
