import pytest

import scraper.core as core
import scraper.exceptions as exceptions
import tests.common as common

import ezscrape.scraper.scraper_requests as scraper_requests


'''
# TODO
!!! DEFINE TESTS, CHECK NEW ONES AND CHECK EXISTING
!!! IMPORT COMMON TEST DATA AND CONSTANTS IF NEEDED
!!! DEFINE PYTEST MARKERS AND DOCUMENT IN PYTEST.INI
'''
def test_requests_scraper_valid_config():
    config = core.ScrapeConfig('url')

    scraper_requests.RequestsScraper._validate_config(config)
    scraper = scraper_requests.RequestsScraper(core.ScrapeConfig('url'))
    assert scraper is not None


REQUESTS_BAD_CONFIG = [
    (common.URL_SINGLE_PAGE_NO_JS, True, False, False),
    (common.URL_SINGLE_PAGE_NO_JS, False, True, False),
    (common.URL_SINGLE_PAGE_NO_JS, False, False, True)
]
@pytest.mark.parametrize('url, javascript, next_page_button_xpath, multi_page', REQUESTS_BAD_CONFIG)
def test_requests_scraper_invalid_config(url, javascript, next_page_button_xpath, multi_page):
    config = core.ScrapeConfig(url)
    config.javascript = javascript
    if next_page_button_xpath:
        config.next_page_button_xpath = 'xpath'
    config.attempt_multi_page = multi_page

    # Failed if We check the Config Directly
    with pytest.raises(exceptions.ScrapeConfigError):
        scraper_requests.RequestsScraper._validate_config(config)

    # Fail if we try to Create the Scraper
    with pytest.raises(exceptions.ScrapeConfigError):
        scraper_requests.RequestsScraper(config)


REQUESTS_GOOD_URLS = [
    (common.URL_SINGLE_PAGE_JS),
    (common.URL_SINGLE_PAGE_JS_DELAYED),
    (common.URL_SINGLE_PAGE_NO_JS),
    (common.URL_MULTI_PAGE_JS_DYNAMIC_LINKS),
    (common.URL_MULTI_PAGE_NO_JS_START_GOOD),
    (common.URL_MULTI_PAGE_JS_STATIC_LINKS_01)
]
@pytest.mark.requests
@pytest.mark.parametrize('url', REQUESTS_GOOD_URLS)
def test_requests_scraper_scrape_ok(url):
    config = core.ScrapeConfig(url)
    scraper = scraper_requests.RequestsScraper(config)
    result = scraper.scrape()

    # Validate Result has the correct Data
    assert result.url == url
    assert result.status == core.ScrapeStatus.SUCCESS
    assert result.request_time_ms > 0
    assert not result.error_msg
    assert len(result) == 1
    assert result._scrape_pages[0].status == core.ScrapeStatus.SUCCESS

    # Validate HTML scraped succesfully
    page = result._scrape_pages[0].html
    assert common.NON_JS_TEST_STRING in page
    assert common.JS_TEST_STRING not in page


REQUESTS_BAD_URLS = [
    (common.URL_BAD_URL),
    (common.URL_URL_NOT_ONLINE)
]
@pytest.mark.requests
@pytest.mark.parametrize('url', REQUESTS_BAD_URLS)
def test_requests_bad_url(url):
    config = core.ScrapeConfig(url)
    scraper = scraper_requests.RequestsScraper(config)
    result = scraper.scrape()

    assert not result
    assert result.url == url
    assert result.error_msg
    assert result.status == core.ScrapeStatus.ERROR


@pytest.mark.requests
def test_requests_scraper_scrape_timeout():
    config = core.ScrapeConfig(common.URL_TIMEOUT)
    config.request_timeout = 2
    scraper = scraper_requests.RequestsScraper(config)
    result = scraper.scrape()

    assert not result
    assert result.status == core.ScrapeStatus.TIMEOUT
    assert result.error_msg is not None
    assert not result
    assert result.request_time_ms < (config.request_timeout + 0.5) * 1000  # Account for function overhead
