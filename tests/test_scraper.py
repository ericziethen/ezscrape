#!/usr/bin/env python3

import pytest

from urllib.parse import urljoin

import scraper

LOCAL_SERVER_HTTP = R'http://127.0.0.1:8000'

SERVER_FILE_SINGLE_PAGE_JS = urljoin(LOCAL_SERVER_HTTP, 'SinglePageJS.html')
SERVER_FILE_SINGLE_PAGE_NO_JS = urljoin(LOCAL_SERVER_HTTP, 'SinglePageNoJS.html')
SERVER_FILE_MULTI_PAGE_JS_START_GOOD = urljoin(LOCAL_SERVER_HTTP, 'MultiPageJS_1.html')
SERVER_FILE_MULTI_PAGE_NO_JS_START_GOOD = urljoin(LOCAL_SERVER_HTTP, 'MultiPageNoJS_1.html')
JS_TEST_STRING = 'LOADED-Javascript Line'
NON_JS_TEST_STRING = 'NON-Javascript Line'

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
URL_ONLINE = [
    ('https://www.hackthissite.org/')
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


########################################
# Tests for Fuction scrape_url
########################################
# Good Download Tests - Single + Multi Page
GOOD_REQUESTS_PARAM_COMBOS = [
    #(SERVER_FILE_SINGLE_PAGE_JS, True, True, 1),
    #(SERVER_FILE_SINGLE_PAGE_JS, False, False, 1),
    #(SERVER_FILE_SINGLE_PAGE_NO_JS, False, False, 1),
    #(SERVER_FILE_SINGLE_PAGE_NO_JS, True, False, 1),
    (SERVER_FILE_MULTI_PAGE_JS_START_GOOD, True, True, 10),
    #(SERVER_FILE_MULTI_PAGE_JS_START_GOOD, False, False, 1),
    #(SERVER_FILE_MULTI_PAGE_NO_JS_START_GOOD, False, False, 3),
    #(SERVER_FILE_MULTI_PAGE_NO_JS_START_GOOD, True, False, 3)
]
@pytest.mark.eric
@pytest.mark.parametrize('url, load_javascript, expect_javascript, page_count', GOOD_REQUESTS_PARAM_COMBOS)
def test_good_page_requests(url, load_javascript, expect_javascript, page_count):
    # First make sure our local server is reachable
    assert scraper.check_url(LOCAL_SERVER_HTTP, local_only=True)

    # Scrape the Page
    result = scraper.scrape_url(url, load_javascript=load_javascript)
    assert result
    assert result.result_good

    # The expected number of pages found
    assert len(result.html_pages) == page_count

    # Search String Found
    for idx, page in enumerate(result.html_pages):
        print(F'CHECK PAGE: {idx}, page: "{page}"')
        assert NON_JS_TEST_STRING in page

        if expect_javascript:
            assert JS_TEST_STRING in page
        else:
            assert JS_TEST_STRING not in page

        if page_count > 1:
            assert F'THIS IS PAGE {idx+1}/3' in page


# Download Tests - Multi-Page



# Special Download Tests - Single-Page



# Special Bad Download Tests - Multi-Page





'''
!!! MINIMUM TESTS NEEDED
    - 1.) Good Requests to Single Page Websites
        - Download a Normal HTML Website (Use Local Test Server and Test File to Download) and check data
        - Download a Javascript HTML Website (Use Local Test Server and Test File to Download) and check data
            -> Verify COntent of Donloaded Url, e.g. HTML or text file etc

    - 2.) Good Requests to Multi Page Websites
        - Download a Normal HTML Website with Multiple Pages (Use Local Test Server and Test File to Download)
        - Download a Javascript HTML Website (with Multiple Pages (Use Local Test Server and Test File to Download) and check data
            -> Verify COntent of Donloaded Url, e.g. HTML or text file etc

    - 3.) Bad Requests to Websites,
        - Javascript Content but not loaded
        - File not Found on server (invalid url)
        - Non Supported Proxy Protocol
        - Unreachable Proxy
        - Multi Page error (no Javascript)
        - Multi Page error (Javascript)
        - No Url Provided
        - Server not Reachable

    - 4.) Proxy Testing, maybe make skippable
        -> Single Test Function, parametrize - parameters
            url, proxy_env, javascript
        -> All Tests, check for specific proxy in environment variable (parametrize)
        -> Skip test if environment variable not set
        -> Environment Variable should set a working Proxy
        -> Target Url is some sort of What's my IP
            - Ideally 1 with Javascript and 1 without (Maybe 2 functions to parse, or check in content)
            - Ideally use 1 with HTTPS and 1 with HTTP (Can be same if supports)
            -> SEE: https://stackoverflow.com/questions/391979/how-to-get-clients-ip-address-using-javascript
        -> CHeck that the IP is actually displayed of that of the Proxy in the response
        - Use Different kind of Proxies
            - HTTP
            - HTTPS
            - SOCKS4
            - SOCKS5





















################################
# Tests for Custom Exceptions
################################



################################
# Tests for Class DownloadResult
################################



################################
# Tests for Fuction download_url
################################




















>>>>>>>>>>>>>>>>>>>>>>> UNSORTED - TOO RAW <<<<<<<<<<<<<<<<<<<<<<<





# Good Tests - Direct Download

GOOD_DOWNLOAD = {
    (R'', , )
}
@pytest.parametrize('url, proxy, javascript', GOOD_DOWNLOAD)
def test_good_download_single_page(url, proxy, javascript):
    result = scraper.download_url(url, proxy_url=proxy, javascript=javascript)


- parametrize the url and proxy information
- Download a Normal HTML Website (Use Local Test Server and Test File to Download) and check data
    -> Criteria: Have the Data from the Page
    - 1.) HTTP Server, Direct
    - 2.) HTTP with HTTP Proxy
    - 3.) HTTP with HTTPS Proxy
    - 4.) HTTP with SOCKS4 Proxy
    - 5.) HTTP with SOCKS5 Proxy
    - 6.) HTTPS Server, Direct
    - 7.) HTTPS with HTTP Proxy
    - 8.) HTTPS with HTTPS Proxy
    - 9.) HTTPS with SOCKS4 Proxy
    - 10.) HTTPS with SOCKS5 Proxy

- parametrize the url and proxy information
- Download a Javascript HTML Website (Use Local Test Server and Test File to Download) and check data
    -> Criteria: Have the Javascript Data from the Page
    - 1.) HTTP Server, Direct
    - 2.) HTTP with HTTP Proxy
    - 3.) HTTP with HTTPS Proxy
    - 4.) HTTP with SOCKS4 Proxy
    - 5.) HTTP with SOCKS5 Proxy
    - 6.) HTTPS Server, Direct
    - 7.) HTTPS with HTTP Proxy
    - 8.) HTTPS with HTTPS Proxy
    - 9.) HTTPS with SOCKS4 Proxy
    - 10.) HTTPS with SOCKS5 Proxy

- parametrize the url and proxy information
- Download a Normal HTML Website with Multiple Pages (Use Local Test Server and Test File to Download)
    -> Criteria: Have the Data from all Pages
    - 1.) HTTP Server, Direct
    - 2.) HTTP with HTTP Proxy
    - 3.) HTTP with HTTPS Proxy
    - 4.) HTTP with SOCKS4 Proxy
    - 5.) HTTP with SOCKS5 Proxy
    - 6.) HTTPS Server, Direct
    - 7.) HTTPS with HTTP Proxy
    - 8.) HTTPS with HTTPS Proxy
    - 9.) HTTPS with SOCKS4 Proxy
    - 10.) HTTPS with SOCKS5 Proxy

- parametrize the url and proxy information
- Download a Javascript HTML Website (with Multiple Pages (Use Local Test Server and Test File to Download) and check data
    -> Criteria: Have the Data from all Javascript Pages
    - 1.) HTTP Server, Direct
    - 2.) HTTP with HTTP Proxy
    - 3.) HTTP with HTTPS Proxy
    - 4.) HTTP with SOCKS4 Proxy
    - 5.) HTTP with SOCKS5 Proxy
    - 6.) HTTPS Server, Direct
    - 7.) HTTPS with HTTP Proxy
    - 8.) HTTPS with HTTPS Proxy
    - 9.) HTTPS with SOCKS4 Proxy
    - 10.) HTTPS with SOCKS5 Proxy


# Proxy Verification Tests
- Tests to verify that Proxies are used, so maybe we can return the caller IP if we can have 2 for our proxies


# Bad Tests

- Download a Normal HTTP Website with Multiple Pages (Some Pages Failed)
- Failed Download of a Website (Custom Exception Raised, with details Provided)
    - Define Different Input Scenarios where Download Fails
        - e.g. File not File Not found
        - invalid address
        - invalid proxy
        - no url provided
'''

