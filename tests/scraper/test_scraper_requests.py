import pytest

import ezscrape.scraper.scraper_requests as scraper

'''
# TODO
!!! DEFINE TESTS, CHECK NEW ONES AND CHECK EXISTING
!!! IMPORT COMMON TEST DATA AND CONSTANTS IF NEEDED
!!! DEFINE PYTEST MARKERS AND DOCUMENT IN PYTEST.INI
'''
'''
def test_requests_scraper_valid_config():


REQUESTS_BAD_CONFIG = [
    (URL_SINGLE_PAGE_NO_JS, True, False, False),
    (URL_SINGLE_PAGE_NO_JS, False, True, False),
    (URL_SINGLE_PAGE_NO_JS, False, False, True)
]
@pytest.mark.parametrize('url, javascript, next_page_button_xpath, multi_page', REQUESTS_BAD_CONFIG)
def test_requests_scraper_invalid_config(url, javascript, next_page_button_xpath, multi_page):
    config = scraper.ScrapeConfig(url)
    config.javascript = javascript
    if next_page_button_xpath:
        config.next_page_button_xpath = 'xpath'
    config.attempt_multi_page = multi_page

    # Failed if We check the Config Directly
    with pytest.raises(scraper.ScrapeConfigError):
        scraper._scrape_url_requests(config)

    # Fail if we try to Create the Scraper


def test_requests_scraper_create_ok():


def test_requests_scraper_create_failed_invalid_config():





def test_requests_scraper_scrape_ok():


def test_requests_scraper_scrape_bad_url():


def test_requests_scraper_scrape_timeout():
'''




