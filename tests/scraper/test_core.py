import pytest

import scraper.core as core
import scraper.exceptions as exceptions


def test_scrape_config_default_values_set():
    url = 'fake_url'
    config = core.ScrapeConfig(url)
    
    assert config.url == url
    assert config.request_timeout == core.DEFAULT_REQUEST_TIMEOUT
    assert config.javascript_wait == core.DEFAULT_JAVASCRIPT_WAIT
    assert config.max_pages == core.DEFAULT_MAX_PAGES
    assert config.next_page_timeout == core.DEFAULT_NEXT_PAGE_TIMEOUT
    assert config.proxy_server is None
    assert config.useragent is None
    assert config.next_page_button_xpath is None
    assert not config.javascript
    assert not config.attempt_multi_page


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
    result.add_scrape_page('html1')
    assert len(result) == 1
    result.add_scrape_page('html2')
    assert len(result) == 2
    result.add_scrape_page('html3')
    assert len(result) == 3


def test_scrape_result_multiple_pages_added():
    result = core.ScrapeResult('url')

    entries = ['html1', 'html2', 'html3']
    result.add_scrape_page(entries[0])
    result.add_scrape_page(entries[1])
    result.add_scrape_page(entries[2])

    for idx, page in enumerate(result):
        assert page.html == entries[idx]


def test_scrape_result_overall_request_time():
    result = core.ScrapeResult('url')
    result.add_scrape_page('html1', scrape_time=100)
    result.add_scrape_page('html2', scrape_time=300)
    result.add_scrape_page('html3', scrape_time=400)

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
