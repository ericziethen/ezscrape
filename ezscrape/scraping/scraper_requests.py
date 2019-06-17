#!/usr/bin/env python3

"""Module to provie Scrape functionality using the requests module."""

import datetime
import http
import logging
import socket

import requests

import scraping.core as core
import scraping.exceptions as exceptions

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class RequestsScraper(core.Scraper):
    """Implement the Scraper using requests."""

    def __init__(self, config: core.ScrapeConfig):
        """Initialize the Request Scraper."""
        super().__init__(config)
        self._caller_ip = None

    def scrape(self) -> core.ScrapeResult:
        """Scrape using Requests."""
        result = core.ScrapeResult(self.config.url)

        # Prepare the Request Data
        headers = {'User-Agent': core.generic_useragent()}
        proxies = {}
        hooks = {'response': self._get_caller_ip}

        if self.config.useragent:
            headers['User-Agent'] = self.config.useragent

        # TODO - Need to Specify Both Possible Proxies
        # TODO - SPECIFY 1 or 2 PROXIES HERE???
        if self.config.proxy_http:
            proxies['http'] = self.config.proxy_http
        if self.config.proxy_https:
            proxies['http'] = self.config.proxy_https

        # Make the Request
        time = datetime.datetime.now()
        try:
            resp = requests.request('get',
                                    self.config.url,
                                    timeout=self.config.request_timeout,
                                    proxies=proxies,
                                    headers=headers,
                                    hooks=hooks,
                                    verify=False)

        except (requests.exceptions.ProxyError,
                requests.exceptions.SSLError) as error:
            result.status = core.ScrapeStatus.PROXY_ERROR
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        except requests.exceptions.Timeout as error:
            result.status = core.ScrapeStatus.TIMEOUT
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        except requests.RequestException as error:
            result.status = core.ScrapeStatus.ERROR
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        else:
            result.caller_ip = self._caller_ip

            # Decide if Success or Not
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as error:
                result.status = core.ScrapeStatus.ERROR
                result.error_msg = (
                    F'HTTP Error: {resp.status_code} - '
                    F'{http.HTTPStatus(resp.status_code).phrase}')
            else:
                result.status = core.ScrapeStatus.SUCCESS
                timediff = datetime.datetime.now() - time
                scrape_time = (timediff.total_seconds() * 1000 +
                               timediff.microseconds / 1000)
                result.add_scrape_page(resp.text, scrape_time=scrape_time,
                                       status=core.ScrapeStatus.SUCCESS)

            resp.close()
        return result

    def _get_caller_ip(self, response, *args, **kwargs) -> None:
        """Get the caller IP from the raw socket."""
        # pylint: disable=unused-argument
        sock = socket.fromfd(response.raw.fileno(), socket.AF_INET,
                             socket.SOCK_STREAM)
        print('SOCKET:', sock)
        self._caller_ip = sock.getsockname()[0]

    @classmethod
    def _validate_config(cls, config: core.ScrapeConfig) -> None:
        """Verify the config can be scraped by requests."""
        if config.javascript:
            raise exceptions.ScrapeConfigError("No Support for Javascript")

        if config.attempt_multi_page or config.wait_for_xpath:
            raise exceptions.ScrapeConfigError(
                "No Support for Multipages, check fields")
