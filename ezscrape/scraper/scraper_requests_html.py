#!/usr/bin/env python3

"""Module to provie Scrape functionality using the requests-html module."""

import datetime
import http
import logging

import requests
import requests_html

import scraper.core as core
import scraper.exceptions as exceptions

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class RequestsHtmlScraper(core.Scraper):
    """Implement the Scraper using requests-html."""

    def scrape(self) -> core.ScrapeResult:
        """Scrape using Requests-Html."""
        result = core.ScrapeResult(self.config.url)
        session = requests_html.HTMLSession()

        next_url = self.config.url
        count = 0
        while next_url is not None:
            logger.debug(F'Processing Url: "{next_url}"')
            count += 1

            # TODO - What if we have multiple pages?, do we need the request time for each?
            # Fire the Request
            time = datetime.datetime.now()
            try:
                resp = session.get(
                    next_url, timeout=self.config.request_timeout)
            except requests.RequestException as err:
                result.error_msg = F'EXCEPTION: {type(err).__name__} - {err}'
            else:
                if self.config.javascript:
                    resp.html.render(sleep=self.config.javascript_wait)
                if resp.status_code == 200:
                    timediff = datetime.datetime.now() - time
                    scrape_time = (timediff.total_seconds() * 1000 +
                                   timediff.microseconds / 1000)
                    result.add_scrape_page(resp.html.html,
                                           scrape_time=scrape_time,
                                           success=True)
                else:
                    result.error_msg = (
                        F'HTTP Error: {resp.status_code} - '
                        F'{http.HTTPStatus(resp.status_code).phrase}')

            if count > self.config.max_pages:
                logger.debug(F'Paging limit of {self.config.max_pages} '
                            'reached, stop scraping')
                break

            if not self.config.attempt_multi_page:
                logger.debug((F'Multipage is not set, skip after first page'))
                break

            next_url = resp.html.next()

        return result

    def _validate_config(self) -> bool:
        """Verify the config can be scraped by requests-html."""
        if self.config.next_page_button_xpath is not None:
            raise exceptions.ScrapeConfigError(
                "No Suport for Next pages via Xpath")
