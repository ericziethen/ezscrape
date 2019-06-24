import pytest

import scraping.core as core
import scraping.exceptions as exceptions


def test_WaitForPageLoad_ok():
    core.WaitForPageLoad('', core.WaitForPageElem.XPATH)
    core.WaitForPageLoad('xpath-text', core.WaitForPageElem.XPATH)


def test_WaitForPageLoad_invalid_text():
    with pytest.raises(ValueError):
        core.WaitForPageLoad(15, core.WaitForPageElem.XPATH)

    with pytest.raises(ValueError):
        core.WaitForPageLoad(None, core.WaitForPageElem.XPATH)

    elem = core.WaitForPageLoad('', core.WaitForPageElem.XPATH)
    with pytest.raises(ValueError):
        elem.wait_text = 15


def test_WaitForPageLoad_invalid_type():
    with pytest.raises(ValueError):
        core.WaitForPageLoad('', 15)

    with pytest.raises(ValueError):
        core.WaitForPageLoad('', None)

    elem = core.WaitForPageLoad('', core.WaitForPageElem.XPATH)
    with pytest.raises(ValueError):
        elem.wait_type = 15


def test_scrape_config_default_values_set():
    url = 'fake_url'
    config = core.ScrapeConfig(url)
    
    assert config.url == url
    assert config.request_timeout == core.DEFAULT_REQUEST_TIMEOUT
    assert config.max_pages == core.DEFAULT_MAX_PAGES
    assert not config.proxy_http
    assert not config.proxy_https
    assert config.useragent is None
    assert not config.xpath_next_button


@pytest.mark.parametrize('invalid_url', [None, '', 15])
def test_scrape_config_set_invalid_url(invalid_url):
    with pytest.raises(exceptions.ScrapeConfigError):
        core.ScrapeConfig(invalid_url)

    valid_config = core.ScrapeConfig('valid_url')
    with pytest.raises(exceptions.ScrapeConfigError):
        valid_config.url = invalid_url


def test_scrape_result_no_pages():
    result = core.ScrapeResult('url')
    assert not bool(result)


def test_scrape_result_page_count():
    result = core.ScrapeResult('url')
    assert len(result) == 0
    result.add_scrape_page('html1', status=core.ScrapeStatus.SUCCESS)
    assert len(result) == 1
    result.add_scrape_page('html2', status=core.ScrapeStatus.SUCCESS)
    assert len(result) == 2
    result.add_scrape_page('html3', status=core.ScrapeStatus.SUCCESS)
    assert len(result) == 3


def test_scrape_result_multiple_pages_added():
    result = core.ScrapeResult('url')

    entries = ['html1', 'html2', 'html3']
    result.add_scrape_page(entries[0], status=core.ScrapeStatus.SUCCESS)
    result.add_scrape_page(entries[1], status=core.ScrapeStatus.SUCCESS)
    result.add_scrape_page(entries[2], status=core.ScrapeStatus.SUCCESS)

    for idx, page in enumerate(result):
        assert page.html == entries[idx]


def test_scrape_result_overall_request_time():
    result = core.ScrapeResult('url')
    result.add_scrape_page('html1', status=core.ScrapeStatus.SUCCESS, scrape_time=100)
    result.add_scrape_page('html2', status=core.ScrapeStatus.SUCCESS, scrape_time=300)
    result.add_scrape_page('html3', status=core.ScrapeStatus.SUCCESS, scrape_time=400)

    assert result.request_time_ms == 800


def test_scraper_scrape_not_implemented():
    scraper = core.Scraper(core.ScrapeConfig('url'))

    with pytest.raises(NotImplementedError):
        scraper.scrape()

def test_scraper_valid_config():
    config = core.ScrapeConfig('url')

    core.Scraper._validate_config(config)
    scraper = core.Scraper(core.ScrapeConfig('url'))
    assert scraper is not None


def test_scraper_invalid_config():
    with pytest.raises(ValueError):
        core.Scraper._validate_config(None)

    with pytest.raises(ValueError):
        core.Scraper(None)

    scraper = core.Scraper(core.ScrapeConfig('url'))
    with pytest.raises(ValueError):
        scraper.config = None
