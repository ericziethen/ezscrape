import pytest

import scraping.scraper as scraper
import scraping.core as core
import scraping.exceptions as exceptions
import tests.common as common

########################################
# Tests for Fuction scrape_url
########################################
@pytest.mark.requests # This could potentially change
def test_scrape_url_scraper_no_js():
    url = common.URL_SINGLE_PAGE_NO_JS
    result = scraper.scrape_url(core.ScrapeConfig(url))

    # Validate Result has the correct Data
    assert result.url == url
    assert result.status == core.ScrapeStatus.SUCCESS
    assert not result.error_msg
    assert len(result) == 1
    assert result._scrape_pages[0].status == core.ScrapeStatus.SUCCESS

    # Validate HTML scraped succesfully
    page = result._scrape_pages[0].html
    assert common.NON_JS_TEST_STRING in page
    assert common.JS_TEST_STRING not in page

@pytest.mark.eric
@pytest.mark.selenium # This could potentially change
def test_scrape_url_scraper_js():
    url = common.URL_SINGLE_PAGE_JS
    config = core.ScrapeConfig(url)
    config.xpath_wait_for_loaded = '''//p[@id='wait-text']'''
    result = scraper.scrape_url(config)

    assert result.url == url
    assert result.status == core.ScrapeStatus.SUCCESS
    assert not result.error_msg
    assert len(result) == 1
    page = result._scrape_pages[0].html

    assert common.NON_JS_TEST_STRING in page
    assert common.JS_TEST_STRING in page


########################################
# Tests for Fuction is_local_address
########################################
IS_LOCAL_ADDRESS = [
    (True, '0.0'),
    (True, '0.0.0.0'),
    (True, '127.1'),
    (True, '127.0.0.1'),
    (True, 'localhost'),
    (True, 'http://localhost'),
    (True, 'http://localhost:8080'),
    (True, 'http://127.0.0.1'),
    (True, '192.168.0.0'),
    (True, '192.168.255.255'),
    (True, '172.16.0.0'),
    (True, '172.31.255.255'),
    (False, '192.167.255.255'),
    (False, '192.169.0.0'),
    (False, '172.15.255.255'),
    (False, '172.32.0.0'),
    (False, 'www.google.com'),
    (False, 'http://www.google.com'),
    (False, 'https://www.google.com'),
    (False, '15.1.1.1'),
    (False, '8.8.8.8')
]
@pytest.mark.parametrize('is_local, url', IS_LOCAL_ADDRESS)
def test_is_local_address(is_local, url):
    assert scraper.is_local_address(url) == is_local


########################################
# Tests for Fuction check_url
########################################
def test_local_test_server_running():
    assert scraper.check_url(common.LOCAL_SERVER_HTTP, local_only=True)


URL_ONLINE = [
    ('https://www.web.de/')
]
@pytest.mark.parametrize('url', URL_ONLINE)
@pytest.mark.webtest
def test_check_url_online(url):
    assert scraper.check_url(url, local_only=False)


URL_FAILED = [
    ('https://www.hackthissite.org/'),
    ('INVALID_URL')
]
@pytest.mark.parametrize('url', URL_FAILED)
def test_check_url_local_only_exception(url):
    with pytest.raises(ValueError):
        scraper.check_url(url, local_only=True)
