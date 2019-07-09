import pytest

import scraping.core as core
import scraping.exceptions as exceptions
import tests.common as common

import ezscrape.scraping.scraper_selenium as scraper_selenium


def test_selenium_scraper_valid_config():
    config = core.ScrapeConfig('url')
    config.javascript = True
    config.attempt_multi_page = True
    config.wait_for_xpath = 'xpath'

    scraper_selenium.SeleniumChromeScraper._validate_config(config)
    scraper = scraper_selenium.SeleniumChromeScraper(config)
    assert scraper is not None


def test_requests_html_scraper_invalid_config():
    config = core.ScrapeConfig('url')

    # Failed if We check the Config Directly
    with pytest.raises(exceptions.ScrapeConfigError):
        scraper_selenium.SeleniumChromeScraper._validate_config(config)

    # Fail if we try to Create the Scraper
    with pytest.raises(exceptions.ScrapeConfigError):
        scraper_selenium.SeleniumChromeScraper(config)


SELENIUM_CHROME_GOOD_URLS_SINGLE_PAGE = [
    (common.URL_SINGLE_PAGE_JS, True),
    (common.URL_SINGLE_PAGE_JS_DELAYED, True),
    (common.URL_SINGLE_PAGE_NO_JS, False),
    (common.URL_MULTI_PAGE_JS_STATIC_LINKS_01, True),
    (common.URL_MULTI_PAGE_JS_STATIC_LINKS_WITH_STATE_01, True),
    (common.URL_MULTI_PAGE_JS_DYNAMIC_LINKS, True),
    (common.URL_MULTI_PAGE_NO_JS_START_GOOD, False)
]
@pytest.mark.slow
@pytest.mark.selenium
@pytest.mark.parametrize('url, javascript', SELENIUM_CHROME_GOOD_URLS_SINGLE_PAGE)
def test_selenium_scraper_scrape_ok_single_page(url, javascript):
    config = core.ScrapeConfig(url)
    config.wait_for_xpath = '/html'
    result = scraper_selenium.SeleniumChromeScraper(config).scrape()

    assert result.url == url
    assert result.status == core.ScrapeStatus.SUCCESS
    assert result.request_time_ms > 0
    assert not result.error_msg
    assert len(result) == 1
    page = result._scrape_pages[0].html

    assert common.NON_JS_TEST_STRING in page
    if javascript:
        assert common.JS_TEST_STRING in page
    else:
        assert common.JS_TEST_STRING not in page


@pytest.mark.slow
@pytest.mark.selenium
def test_selenium_scraper_scrape_paging():
    config = core.ScrapeConfig(common.URL_MULTI_PAGE_JS_STATIC_LINKS_WITH_STATE_01)
    config.wait_for_xpath = R'''//a[@title='next' and @class='enabled']'''
    config.next_page_timeout = 0
    config.attempt_multi_page = True
    result = scraper_selenium.SeleniumChromeScraper(config).scrape()
    assert len(result) == 2

    for idx, scrape_result in enumerate(result, start=1):
        assert F'THIS IS PAGE {idx}/2' in scrape_result.html
        if idx == len(result):  # Timeout because of last page
            assert scrape_result.status == core.ScrapeStatus.TIMEOUT
        else:
            assert scrape_result.status == core.ScrapeStatus.SUCCESS


@pytest.mark.slow
@pytest.mark.selenium
def test_selenium_chrome_good_scrape_max_next_page_reached():
    config = core.ScrapeConfig(common.URL_MULTI_PAGE_JS_STATIC_LINKS_01)
    config.wait_for_xpath = '''//a[@title='next']'''
    config.request_timeout = 2
    config.attempt_multi_page = True
    result = scraper_selenium.SeleniumChromeScraper(config).scrape()
    assert len(result) == core.DEFAULT_MAX_PAGES


@pytest.mark.slow
@pytest.mark.selenium
def test_selenium_chrome_context_manager_good_scrape():
    url_list = [common.URL_SINGLE_PAGE_JS, common.URL_SINGLE_PAGE_NO_JS]
    with scraper_selenium.SeleniumChromeSession() as chrome_session:
        for url_tup in SELENIUM_CHROME_GOOD_URLS_SINGLE_PAGE:
            url = url_tup[0]
            javascript = url_tup[1]

            config = core.ScrapeConfig(url)
            config.wait_for_xpath = '/html'
            result = scraper_selenium.SeleniumChromeScraper(config, browser=chrome_session).scrape()

            page = result._scrape_pages[0].html
            if javascript:
                assert common.JS_TEST_STRING in page
            else:
                assert common.JS_TEST_STRING not in page


@pytest.mark.selenium
def test_selenium_invalid_url():
    config = core.ScrapeConfig(common.URL_BAD_URL)
    config.wait_for_xpath = 'xpath'
    config.request_timeout = 1
 
    result = scraper_selenium.SeleniumChromeScraper(config).scrape()

    assert result.error_msg
    assert result.status == core.ScrapeStatus.ERROR


@pytest.mark.selenium
def test_selenium_url_not_reachable():
    config = core.ScrapeConfig(common.URL_URL_NOT_ONLINE)
    config.wait_for_xpath = 'xpath'
    config.request_timeout = 1
 
    result = scraper_selenium.SeleniumChromeScraper(config).scrape()

    assert result.error_msg
    assert result.status == core.ScrapeStatus.TIMEOUT


@pytest.mark.slow
@pytest.mark.selenium
def test_selenium_scrape_timeout():
    config = core.ScrapeConfig(common.URL_TIMEOUT)
    config.request_timeout = 2
    config.wait_for_xpath = 'xpath'

    result = scraper_selenium.SeleniumChromeScraper(config).scrape()
    assert not result
    assert result.error_msg
    assert result.request_time_ms < (config.request_timeout + 0.5) * 1000 # Account for functio overhead


@pytest.mark.slow
@pytest.mark.selenium
def test_selenium_limit_pages():
    config = core.ScrapeConfig(common.URL_MULTI_PAGE_NO_JS_START_GOOD)
    config.attempt_multi_page = True
    config.max_pages = 1
    config.wait_for_xpath = 'xpath'

    result = scraper_selenium.SeleniumChromeScraper(config).scrape()

    assert len(result) == config.max_pages


#TODO - ADD SOME PROXY TESTS
