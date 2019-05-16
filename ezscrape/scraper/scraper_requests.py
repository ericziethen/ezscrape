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
        try:
            resp = requests.request('get', self.config.url,
                                    timeout=self.config.request_timeout)
        except requests.RequestException as error:
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        else:
            if resp.status_code == 200:
                timediff = datetime.datetime.now() - time
                scrape_time = (timediff.total_seconds() * 1000 +
                               timediff.microseconds / 1000)
                result.add_scrape_page(resp.text, scrape_time=scrape_time,
                                       success=True)
            else:
                result.error_msg = (
                    F'HTTP Error: {resp.status_code} - '
                    F'{http.HTTPStatus(resp.status_code).phrase}')
        return result

    def _validate_config(self) -> bool:
        """Verify the config can be scraped by requests."""
        if self.config.javascript:
            raise exceptions.ScrapeConfigError("No Support for Javascript")

        if (self.config.attempt_multi_page or
                (self.config.next_page_button_xpath is not None)):
            raise exceptions.ScrapeConfigError(
                "No Support for Multipages, check fields")
