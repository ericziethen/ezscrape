#!/usr/bin/env python3

import urllib.parse

from typing import Type
from urllib.parse import urljoin

from bs4 import BeautifulSoup

import scraping.core as core

LOCAL_SERVER_HTTP = R'http://127.0.0.1:8000'

JS_TEST_STRING = 'LOADED-Javascript Line'
NON_JS_TEST_STRING = 'NON-Javascript Line'
URL_SINGLE_PAGE_JS = urljoin(LOCAL_SERVER_HTTP, 'SinglePageJS.html')
URL_SINGLE_PAGE_JS_DELAYED = urljoin(LOCAL_SERVER_HTTP, 'SinglePageJS_Delayed.html')
URL_SINGLE_PAGE_NO_JS = urljoin(LOCAL_SERVER_HTTP, 'SinglePageNoJS.html')
URL_MULTI_PAGE_JS_DYNAMIC_LINKS = urljoin(LOCAL_SERVER_HTTP, 'MultiPageJS_DynamicLinks.html')
URL_MULTI_PAGE_NO_JS_START_GOOD = urljoin(LOCAL_SERVER_HTTP, 'MultiPageNoJS_1.html')
URL_MULTI_PAGE_JS_STATIC_LINKS_01 = urljoin(LOCAL_SERVER_HTTP, 'MultiPageJS_STATIC_LINKS_1.html')
URL_MULTI_PAGE_JS_STATIC_LINKS_04 = urljoin(LOCAL_SERVER_HTTP, 'MultiPageJS_STATIC_LINKS_4.html')
URL_MULTI_PAGE_JS_STATIC_LINKS_WITH_STATE_01 = urljoin(LOCAL_SERVER_HTTP, 'MultiPageJS_STATIC_LINKS_WITH_STATE_1.html')
URL_MULTI_PAGE_JS_STATIC_LINKS_WITH_STATE_02 = urljoin(LOCAL_SERVER_HTTP, 'MultiPageJS_STATIC_LINKS_WITH_STATE_2.html')

URL_BAD_URL = 'this is not a url'
URL_URL_NOT_ONLINE = urljoin(LOCAL_SERVER_HTTP, 'UrlNotFound.html')
URL_TIMEOUT = 'http://10.255.255.1/'

URL_WHATS_MY_IP_HTTPS = 'https://whatsmyip.com/'
URL_WHATS_MY_IP_HTTP = 'http://whatismyip.host/'


def whatsmyip_ip_from_html(url: str, html: str) -> str:
    """Verify the Default What's my ip address."""
    soup = BeautifulSoup(html)

    if url == URL_WHATS_MY_IP_HTTPS:
        found_ip = soup.find('p', attrs={'id': 'shownIpv4'})
    elif url == URL_WHATS_MY_IP_HTTP:
        found_ip = soup.find('p', attrs={'class': 'ipaddress'})
    else:
        raise ValueError(F'URL: "{url}" not supported for whahts my ip lookup')

    if found_ip:
        return found_ip.string
    else:
        return ''
