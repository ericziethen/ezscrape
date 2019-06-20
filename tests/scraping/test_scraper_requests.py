import pytest

import scraping.core as core
import scraping.exceptions as exceptions
import scraping.web_lib as web_lib
import tests.common as common

import ezscrape.scraping.scraper_requests as scraper_requests


def test_requests_scraper_valid_config():
    config = core.ScrapeConfig('url')

    scraper_requests.RequestsScraper._validate_config(config)
    scraper = scraper_requests.RequestsScraper(config)
    assert scraper is not None


REQUESTS_BAD_CONFIG = [
    (True, False, False),
    (False, True, False),
    (False, False, True)
]
@pytest.mark.parametrize('javascript, xpath_next_button, multi_page', REQUESTS_BAD_CONFIG)
def test_requests_scraper_invalid_config(javascript, xpath_next_button, multi_page):
    config = core.ScrapeConfig('url')
    config.javascript = javascript
    if xpath_next_button:
        config.xpath_next_button = 'xpath'
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

#TODO - ADD SOME PROXY TESTS
#TODO - Proxy List should probably come from Env Variables for testing
#'''
PROXY_LIST = [
    (common.URL_WHATS_MY_IP_HTTPS, 'http://91.208.39.70:8080', 'https://91.208.39.70:8080'),
    (common.URL_WHATS_MY_IP_HTTP, 'http://91.208.39.70:8080', 'https://91.208.39.70:8080'),
    (common.URL_WHATS_MY_IP_HTTPS, 'http://157.230.249.74:3128', 'https://157.230.249.74:3128'),
    (common.URL_WHATS_MY_IP_HTTP, 'http://157.230.249.74:3128', 'https://157.230.249.74:3128'),
    (common.URL_WHATS_MY_IP_HTTPS, 'http://104.248.79.41:3128', 'https://104.248.79.41:3128'),
    (common.URL_WHATS_MY_IP_HTTP, 'http://104.248.79.41:3128', 'https://104.248.79.41:3128'),
    (common.URL_WHATS_MY_IP_HTTPS, 'http://103.6.184.250:54674', 'https://103.6.184.250:54674'),
    (common.URL_WHATS_MY_IP_HTTP, 'http://103.6.184.250:54674', 'https://103.6.184.250:54674')
]
@pytest.mark.proxytest
@pytest.mark.webtest
@pytest.mark.requests
@pytest.mark.parametrize('url, http_proxy, https_proxy', PROXY_LIST)
def test_proxies(url, http_proxy, https_proxy):
    config = core.ScrapeConfig(url)
    config.proxy_http = http_proxy
    config.proxy_https = https_proxy
    scraper = scraper_requests.RequestsScraper(config)
    result = scraper.scrape()

    print('ERROR', result.error_msg)

    assert result

    if url.startswith('http://'):
        assert result.caller_ip == web_lib.split_url(http_proxy).hostname
        proxy_ip = http_proxy
    else:
        assert result.caller_ip == web_lib.split_url(https_proxy).hostname
        proxy_ip = https_proxy

    '''
    page = result._scrape_pages[0]
    print('HTML', page.html)

    html_ip = common.whatsmyip_ip_from_html(url, page.html)
    print('foundIP:', html_ip)
    assert html_ip == proxy_ip
    '''
#'''
