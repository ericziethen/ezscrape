#!/usr/bin/env python3

!!! DELETE ME ONCE ALL CLEANED UP !!!


"""Provide Website downloading functionality."""

'''
!!! MOVE FUNCTIONALITY INTO SUB package
    /ezscrape/
              scraper/
                      scraper_definitions.py    -> Classes, Exceptions etc
                      scraper_requests.py       -> Requests
                      scraper_requests_html.py  -> Requests-HTML
                      scraper_selenium.py       -> Selenium
                      scraper.py                -> Combine all available scrapers
    1.) Make sure all non slow and non web tests ok, at least most
    2.) Copy Definitions file
        - change existing files that use them
        - make the tests work
    3.) Copy Requests
        - change existing files that use them
        - make the tests work
        - split tests
    4.) Copy Requests-HTML
        - change existing files that use them
        - make the tests work
        - split tests
    5.) Copy Selenium
        - change existing files that use them
        - make the tests work
        - split tests
    

'''

import datetime
import enum
import http
import ipaddress
import logging
import os
import requests
import requests_html
import sys
import urllib.parse


from typing import Iterator, Optional

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name



























































##############################################################
#
###### OLD IMPLEMENTATION - REFACTOR
#
##############################################################





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
        self.max_pages = sys.maxsize
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

'''
