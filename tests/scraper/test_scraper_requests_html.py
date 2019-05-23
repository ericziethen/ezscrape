import pytest

import scraper.core as core
import scraper.exceptions as exceptions
import tests.common as common

import ezscrape.scraper.scraper_requests_html as scraper_requests_html


def test_requests_html_scraper_valid_config():
    config = core.ScrapeConfig('url')
    config.javascript = True
    config.attempt_multi_page = True

    scraper_requests_html.RequestsHtmlScraper._validate_config(config)
    scraper = scraper_requests_html.RequestsHtmlScraper(config)
    assert scraper is not None


def test_requests_html_scraper_invalid_config():
    config = core.ScrapeConfig('url')
    config.wait_for_xpath = 'xpath'

    # Failed if We check the Config Directly
    with pytest.raises(exceptions.ScrapeConfigError):
        scraper_requests_html.RequestsHtmlScraper._validate_config(config)

    # Fail if we try to Create the Scraper
    with pytest.raises(exceptions.ScrapeConfigError):
        scraper_requests_html.RequestsHtmlScraper(config)


# TODO - THis is a reasonable complex test setup, maybe split in multiple tests
REQUESTS_HTML_GOOD_URLS = [
    (common.URL_SINGLE_PAGE_JS, True, True, 1),
    (common.URL_SINGLE_PAGE_JS, False, False, 1),
    (common.URL_SINGLE_PAGE_JS_DELAYED, True, True, 1),
    (common.URL_SINGLE_PAGE_JS_DELAYED, False, False, 1),
    (common.URL_SINGLE_PAGE_NO_JS, False, False, 1),
    (common.URL_SINGLE_PAGE_NO_JS, True, False, 1),
    (common.URL_MULTI_PAGE_JS_STATIC_LINKS_01, True, True, 1),
    (common.URL_MULTI_PAGE_JS_DYNAMIC_LINKS, True, True, 1),
    (common.URL_MULTI_PAGE_JS_DYNAMIC_LINKS, False, False, 1),
    (common.URL_MULTI_PAGE_NO_JS_START_GOOD, False, False, 3),
    (common.URL_MULTI_PAGE_NO_JS_START_GOOD, True, False, 3)
]
@pytest.mark.requests_html
@pytest.mark.parametrize('url, load_javascript, expect_javascript, expected_page_count', REQUESTS_HTML_GOOD_URLS)
def test_requests_html_scraper_scrape_ok(url, load_javascript, expect_javascript, expected_page_count):
    config = core.ScrapeConfig(url)
    config.javascript = load_javascript
    config.javascript_wait = 0.2
    if expected_page_count > 1:
        config.attempt_multi_page = True

    result = scraper_requests_html.RequestsHtmlScraper(config).scrape()

    assert result.url == url
    assert result.status == core.ScrapeStatus.SUCCESS
    assert result.request_time_ms > 0
    assert not result.error_msg
    assert len(result) == expected_page_count

    # Search String Found
    for idx, scrape_result in enumerate(result):
        assert scrape_result.status == core.ScrapeStatus.SUCCESS
        page = scrape_result.html
        print(F'CHECK PAGE: {idx}, page: "{page}"')
        assert common.NON_JS_TEST_STRING in page

        if expect_javascript:
            assert common.JS_TEST_STRING in page
        else:
            assert common.JS_TEST_STRING not in page

        if expected_page_count > 1:
            assert F'THIS IS PAGE {idx+1}/{expected_page_count}' in page


REQUESTS_HTML_BAD_URLS = [
    (common.URL_BAD_URL, None, None),
    (common.URL_URL_NOT_ONLINE, None, None)
]
@pytest.mark.requests_html
@pytest.mark.parametrize('url, req_timeout, js_timeout', REQUESTS_HTML_BAD_URLS)
def test_requests_html_bad_url(url, req_timeout, js_timeout):
    config = core.ScrapeConfig(url)
    if req_timeout:
        config.request_timeout = req_timeout
    if js_timeout:
        config.javascript_wait = js_timeout
 
    result = scraper_requests_html.RequestsHtmlScraper(config).scrape()

    assert not result
    assert result.url == url
    assert result.error_msg
    assert result.status == core.ScrapeStatus.ERROR


@pytest.mark.requests_html
def test_requests_html_scraper_scrape_timeout():
    config = core.ScrapeConfig(common.URL_TIMEOUT)
    config.request_timeout = 2

    result = scraper_requests_html.RequestsHtmlScraper(config).scrape()
    assert not result
    assert result.error_msg
    assert result.request_time_ms < (config.request_timeout + 0.5) * 1000 # Account for functio overhead


@pytest.mark.requests_html
def test_requests_html_limit_pages():
    config = core.ScrapeConfig(common.URL_MULTI_PAGE_NO_JS_START_GOOD)
    config.attempt_multi_page = True
    config.max_pages = 1

    result = scraper_requests_html.RequestsHtmlScraper(config).scrape()

    assert len(result) == config.max_pages

#TODO - ADD SOME PROXY TESTS
