import pytest

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import scraping.core as core
import scraping.exceptions as exceptions
import tests.common as common

import ezscrape.scraping.scraper_selenium as scraper_selenium


def test_selenium_scraper_valid_config():
    config = core.ScrapeConfig('url')
    config.javascript = True
    config.attempt_multi_page = True
    config.xpath_next_button = 'xpath'

    scraper_selenium.SeleniumChromeScraper._validate_config(config)
    scraper = scraper_selenium.SeleniumChromeScraper(config)
    assert scraper is not None


def test_selenium_scraper_invalid_config():
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
    config.xpath_next_button = '/html'
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
    config.xpath_next_button = R'''//a[@title='next' and @class='enabled']'''
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
    config.xpath_next_button = '''//a[@title='next']'''
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
            config.xpath_next_button = '/html'
            result = scraper_selenium.SeleniumChromeScraper(config, browser=chrome_session).scrape()

            page = result._scrape_pages[0].html
            if javascript:
                assert common.JS_TEST_STRING in page
            else:
                assert common.JS_TEST_STRING not in page


@pytest.mark.selenium
def test_selenium_invalid_url():
    config = core.ScrapeConfig(common.URL_BAD_URL)
    config.xpath_next_button = 'xpath'
    config.request_timeout = 1
 
    result = scraper_selenium.SeleniumChromeScraper(config).scrape()

    assert result.error_msg
    assert result.status == core.ScrapeStatus.ERROR


@pytest.mark.selenium
def test_selenium_url_not_reachable():
    config = core.ScrapeConfig(common.URL_URL_NOT_ONLINE)
    config.xpath_next_button = 'xpath'
    config.request_timeout = 1
 
    result = scraper_selenium.SeleniumChromeScraper(config).scrape()

    assert result.error_msg
    assert result.status == core.ScrapeStatus.TIMEOUT


@pytest.mark.slow
@pytest.mark.selenium
def test_selenium_scrape_timeout():
    config = core.ScrapeConfig(common.URL_TIMEOUT)
    config.request_timeout = 2
    config.xpath_next_button = 'xpath'

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
    config.xpath_next_button = 'xpath'

    result = scraper_selenium.SeleniumChromeScraper(config).scrape()

    assert len(result) == config.max_pages


def test_class_WaitCondition():
    condition = scraper_selenium.WaitCondition('timeout', (By.XPATH, 'invalid-xpath'),
        scraper_selenium.WaitLogic.MUST_HAVE, scraper_selenium.WaitType.WAIT_FOR_LOCATED)
    assert condition is not None

# TODO def test_class_WaitCondition_invalid(): # Maybe, if decide we need validator


@pytest.mark.selenium
def test_class_ScraperWait_timeout():
    url = common.URL_MULTI_PAGE_JS_STATIC_LINKS_WITH_STATE_01

    condition = scraper_selenium.WaitCondition('timeout', (By.XPATH, 'invalid-xpath'),
        scraper_selenium.WaitLogic.MUST_HAVE, scraper_selenium.WaitType.WAIT_FOR_LOCATED)

    elem = None
    with pytest.raises(TimeoutException):
        with scraper_selenium.SeleniumChromeSession() as chrome_session:
            chrome_session.get(url)

            page = chrome_session.page_source
            assert common.NON_JS_TEST_STRING in page
            assert common.JS_TEST_STRING in page

            elem = WebDriverWait(chrome_session, 3).until(
                scraper_selenium.ScraperWait([condition]))

    assert elem is None


@pytest.mark.selenium
def test_class_ScraperWait_timeout_1_of_2_must_haves():
    url = common.URL_MULTI_PAGE_JS_STATIC_LINKS_WITH_STATE_01

    conditions = []
    conditions.append(scraper_selenium.WaitCondition('1', (By.XPATH, '''//a[@title='prev']'''),
        scraper_selenium.WaitLogic.MUST_HAVE, scraper_selenium.WaitType.WAIT_FOR_LOCATED))
    conditions.append(scraper_selenium.WaitCondition('2', (By.XPATH, 'invalid-xpath'),
        scraper_selenium.WaitLogic.MUST_HAVE, scraper_selenium.WaitType.WAIT_FOR_CLICKABLE))

    elem = None
    with pytest.raises(TimeoutException):
        with scraper_selenium.SeleniumChromeSession() as chrome_session:
            chrome_session.get(url)

            page = chrome_session.page_source
            assert common.NON_JS_TEST_STRING in page
            assert common.JS_TEST_STRING in page

            elem = WebDriverWait(chrome_session, 3).until(
                scraper_selenium.ScraperWait(conditions))

    assert elem is None


SINGLE_WAIT_COMBO = [
    (scraper_selenium.WaitLogic.MUST_HAVE, scraper_selenium.WaitType.WAIT_FOR_LOCATED),
    (scraper_selenium.WaitLogic.OPTIONAL, scraper_selenium.WaitType.WAIT_FOR_LOCATED),
    (scraper_selenium.WaitLogic.MUST_HAVE, scraper_selenium.WaitType.WAIT_FOR_CLICKABLE),
    (scraper_selenium.WaitLogic.OPTIONAL, scraper_selenium.WaitType.WAIT_FOR_CLICKABLE)
]
@pytest.mark.slow
@pytest.mark.selenium
@pytest.mark.parametrize('wait_logic, wait_type', SINGLE_WAIT_COMBO)
def test_class_ScraperWait_logic_type_combos(wait_logic, wait_type):
    url = common.URL_MULTI_PAGE_JS_STATIC_LINKS_WITH_STATE_01

    condition = scraper_selenium.WaitCondition(
        'test', (By.XPATH, '''//a[@title='page1']'''), wait_logic, wait_type)

    with scraper_selenium.SeleniumChromeSession() as chrome_session:
        chrome_session.get(url)
        page = chrome_session.page_source
        elem = WebDriverWait(chrome_session, 3).until(scraper_selenium.ScraperWait([condition]))

        assert elem is not None

        page = chrome_session.page_source
        assert '<a title="prev" class="disabled">prev</a>' in page
        assert '<a title="page1" href="MultiPageJS_STATIC_LINKS_WITH_STATE_1.html" class="enabled">1</a>' in page
        assert '<a title="page2" href="MultiPageJS_STATIC_LINKS_WITH_STATE_2.html" class="enabled">2</a>' in page
        assert 'MultiPageJS_STATIC_LINKS_WITH_STATE_2.html' in page


@pytest.mark.eric
@pytest.mark.selenium
def test_class_ScraperWait_1_of_2_might_haves():
    url = common.URL_MULTI_PAGE_JS_STATIC_LINKS_WITH_STATE_01

    conditions = []
    conditions.append(scraper_selenium.WaitCondition('1', (By.XPATH, '''//a[@title='prev']'''),
        scraper_selenium.WaitLogic.OPTIONAL, scraper_selenium.WaitType.WAIT_FOR_LOCATED))
    conditions.append(scraper_selenium.WaitCondition('2', (By.XPATH, 'invalid-xpath'),
        scraper_selenium.WaitLogic.OPTIONAL, scraper_selenium.WaitType.WAIT_FOR_CLICKABLE))

    elem = None
    with scraper_selenium.SeleniumChromeSession() as chrome_session:
        chrome_session.get(url)

        page = chrome_session.page_source
        assert common.NON_JS_TEST_STRING in page
        assert common.JS_TEST_STRING in page

        scraper_wait = scraper_selenium.ScraperWait(conditions)

        elem = WebDriverWait(chrome_session, 3).until(scraper_wait)

        assert elem is not None
        assert '1' in scraper_wait.found_elements

        my_elem = scraper_wait.found_elements['1']
        assert my_elem == elem
        assert False

# TODO def test_class_ScraperWait_result_populated():


#TODO - ADD SOME PROXY TESTS