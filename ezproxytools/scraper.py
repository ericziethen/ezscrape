#!/usr/bin/env python3

"""Provide Website downloading functionality."""

import ipaddress
import os
import requests_html
import sys
import urllib.error
import urllib.parse
import urllib.request

from typing import Optional

SPECIAL_LOCAL_ADDRESSES = [
    'localhost',
    '0.0',
    '127.1'
]
'''
class ScrapeError(Exception):
    """Generic Page Scrape Error."""


class SeleniumChromeSession():
    """Context Manager for a Selenium Chrome Session."""


class ScrapeConfig():
    """Class to hold scrape config data needed for downloading the html."""


class ScrapeResult():
    """Class to keep the Download Result Data."""


def _scrape_url_requests(config: ScrapeConfig) -> ScrapeResult:
    """Scrape using Requests."""
    raise NotImplementedError

def _scrape_url_requests_html(config: ScrapeConfig) -> ScrapeResult:
    """Scrape using Requests-HTML."""
    raise NotImplementedError


def _scrape_url_selenium_chrome(config: ScrapeConfig,
                                browser=None) -> ScrapeResult:
    """Scrape using Selenium with Chrome."""
    raise NotImplementedError

def scrape_url(config: ScrapeConfig) -> ScrapeResult:
    """Generic function to handle all scraping requests."""
    raise NotImplementedError
'''

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























































##############################################################
#
###### OLD IMPLEMENTATION - REFACTOR
#
##############################################################





'''
'''
class ScrapeError(Exception):
    """Generic Page Scrape Error."""


class ScrapeConfig():
    """Class to hold scrape config data needed for downloading the html."""

    def __init__(self, url) -> None:
        self.url
        self.proxy_server = ''
        self.javascript = False
        self.next_page_xpath = ''
        self.useragent = ''
        self.multipages = False
        self.max_next_pages = sys.maxsize
        self.next_page_timeout = 1
        # TODO - Define more fields whatever might be needed for scraping


class ScrapeResult():
    """Class to keep the Download Result Data."""

    def __init__(self, response):
        """Initialize the Scrape Result."""
        self._response = response               # Selenium Response is different, either subclass or none)
        self.html_pages = []
        self.status_code = response.status_code #(Can't get it from Selenium)
        self.next_page = None

    @property
    def result_good(self) -> bool:
        """Check if the result is ok,"""
        return self.status_code == 200


'''
import requests
from selenium import webdriver

def test_scrape_selenium_chrome(url):
    with webdriver.Chrome(executable_path=R'D:\temp\chromedriver_win32\chromedriver.exe') as browser:
        r = browser.get(url)
        result = ScrapeResult(r)
        result.html_pages.append(browser.page_source)
        return result

def test_scrape_selenium_chrome_headless(url):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')


    with webdriver.Chrome(chrome_options=chrome_options, executable_path=R'D:\temp\chromedriver_win32\chromedriver.exe') as browser:
        r = browser.get(url)
        result = ScrapeResult(r)
        result.html_pages.append(browser.page_source)
        return result

def test_scrape_requests(url):
    r = requests.request('get', url)
    result = ScrapeResult(r)
    result.html_pages.append(r.text)
    return result

def test_scrape_html_requests(url):
    session = requests_html.HTMLSession()
    r = session.get(url)
    result = ScrapeResult(r)
    result.html_pages.append(r.html.html)
    return result
'''
'''
reuse_browser = webdriver.Chrome(executable_path=R'D:\temp\chromedriver_win32\chromedriver.exe')
chrome_options2 = webdriver.ChromeOptions()
chrome_options2.add_argument("--headless")
reuse_browser_headless = webdriver.Chrome(chrome_options=chrome_options2, executable_path=R'D:\temp\chromedriver_win32\chromedriver.exe')
'''
'''
def test_scrape_selenium_chrome_reuse(url):
    r = reuse_browser.get(R'chrome://version/')
    r = reuse_browser.get(url)
    result = ScrapeResult(r)
    result.html_pages.append(reuse_browser.page_source)
    return result

def test_scrape_selenium_chrome_headless_reuse(url):
    r = reuse_browser.get(R'chrome://version/')
    r = reuse_browser_headless.get(url)
    result = ScrapeResult(r)
    result.html_pages.append(reuse_browser_headless.page_source)
    return result




def test_scrape_selenium_chrome_headless_reuse_pass(url, browser):
    r = browser.get(R'chrome://version/')
    r = browser.get(url)
    result = ScrapeResult(r)
    result.html_pages.append(browser.page_source)
    return result
'''



'''
!!! ### SOME PROBLEMS
!!! 1.) If I cannot find a way to not download CHromium automatically, maybe easier
!!! to use headless chromium and then we don't need html-requests but onlye requests
!!! but it might be ok for us to do as well, esecially when using Internally and in an
!!! automated way it should only download once
!!! 2.) It does not do javascript pagination, so if that is essential use selenium for those
!!! 3.) Selenium uses browser "always?", for HTML pages we might just want to use requests-html
!!! 4.) Need to check Timinig, Selenium vs Requests vs HTML-Requests
!!! 5.) The Project should probably be called ezscraper to account for the actual purpose
'''
'''
'''
def scrape_url(url: str, *, proxy_url: Optional[str] = None, wait: float = 0,
               load_javascript: bool = False) -> ScrapeResult:
    """Download the given url with the given proxy if specified."""

    session = requests_html.HTMLSession()
    response = session.get(url)
    if load_javascript:
        response.html.render(wait=wait)

    
    result = ScrapeResult(response)
    print('INITIAL NEXT PAGE:::', response.html.next())
    for html in response.html:
        if load_javascript:
            html.render(wait=wait)
        result.html_pages.append(html.html)
        print(F'ERIC:::"{html.html}"')
        print('NEXT PAGE:::', html.next())

    return result

