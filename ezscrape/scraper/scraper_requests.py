#!/usr/bin/env python3

"""Module to provie Scrape functionality using the requests module."""

import datetime
import http
import logging

import requests

import scraper.core as core
import scraper.exceptions as exceptions

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class RequestsScraper(core.Scraper):
    """Implement the Scraper using requests."""

    def scrape(self) -> core.ScrapeResult:
        """Scrape using Requests."""
        result = core.ScrapeResult(self.config.url)
        time = datetime.datetime.now()
        headers = {}
        if self.config.useragent:
            headers['User-Agent'] = self.config.useragent
        else:
            headers['User-Agent'] = core.generic_useragent()

        proxies = {}
        # TODO - Need to Specify Both Possible Proxies
        if self.config.proxy_server:
            proxies = {'http': self.config.proxy_server,
                       'https': self.config.proxy_server}
        try:
            resp = requests.request('get', self.config.url,
                                    timeout=self.config.request_timeout,
                                    proxies=proxies,
                                    headers=headers)
        except requests.exceptions.Timeout as error:
            result.status = core.ScrapeStatus.TIMEOUT
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        except requests.RequestException as error:
            result.status = core.ScrapeStatus.ERROR
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        else:
            result._raw_response = resp
            if resp.status_code == 200:
                result.status = core.ScrapeStatus.SUCCESS
                timediff = datetime.datetime.now() - time
                scrape_time = (timediff.total_seconds() * 1000 +
                               timediff.microseconds / 1000)
                result.add_scrape_page(resp.text, scrape_time=scrape_time,
                                       status=core.ScrapeStatus.SUCCESS)
            else:
                result.status = core.ScrapeStatus.ERROR
                result.error_msg = (
                    F'HTTP Error: {resp.status_code} - '
                    F'{http.HTTPStatus(resp.status_code).phrase}')
            resp.close()
        return result

    @classmethod
    def _validate_config(cls, config: core.ScrapeConfig) -> None:
        """Verify the config can be scraped by requests."""
        if config.javascript:
            raise exceptions.ScrapeConfigError("No Support for Javascript")

        if config.attempt_multi_page or config.wait_for_xpath:
            raise exceptions.ScrapeConfigError(
                "No Support for Multipages, check fields")
