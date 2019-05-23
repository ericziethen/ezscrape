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

    # TODO - THIS FUNCTION IS NEARLY IDENTICAL TO THE REQUESTS ONE,
    # TODO - MAYBE WE CAN SHARE MORE INSTEAD OF USEING THE SAME
    # THE REAL DIFFERENCE IS THE MULTI PAGES AND SOME SETTINGS
    # TODO - MAYBE HAVE 1 FUNCTION TO CALL THE ACTUAL REQUEST
    # TODO - AND ANOTHER THAT HANDLES THE RESULT, e.g. process_result()
    # THAT CAN BE SHARED BY ALL
    # Maybe even have a function that catches Request exceptions?
    # OR MAYBE LEAVE FOR NOW AND GET IT WORKING
    # TODO - MAYBE HAVE A MODE, SELENIUM AND REQUESTS ONLY IF SELENIUM CAN HANDLE ALL NEXT PAGES
    def scrape(self) -> core.ScrapeResult:
        """Scrape using Requests-Html."""
        result = core.ScrapeResult(self.config.url)
        session = requests_html.HTMLSession()

        next_url = self.config.url
        count = 0

        # HEADER AND STUFF SHOULD COME FROM SEPARATE FUNCTION AND STORED INTERNALLY
        headers = {}
        if self.config.useragent:
            headers['User-Agent'] = self.config.useragent
        else:
            headers['User-Agent'] = core.generic_useragent()

        # TODO - Decide if needed for Proxy Testing, can store in self
        #hooks={'response': self._get_caller_ip}

        # TODO - Need to Specify Both Possible Proxies
        # TODO - SPECIFY 1 or 2 PROXIES HERE???
        proxies = {}
        if self.config.proxy_http:
            proxies['http'] = self.config.proxy_http
        if self.config.proxy_https:
            proxies['http'] = self.config.proxy_https

        while next_url is not None:
            logger.debug(F'Processing Url: "{next_url}"')
            count += 1

            # TODO - What if we have multiple pages?, do we need the request time for each?
            # Fire the Request
            time = datetime.datetime.now()
            try:
                resp = session.get(
                    next_url, timeout=self.config.request_timeout,
                                    proxies=proxies,
                                    headers=headers,
                                    stream=True,
                                    #hooks=hooks,
                                    verify=False)
            except requests.exceptions.Timeout as error:
                result.status = core.ScrapeStatus.TIMEOUT
                result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
            except requests.RequestException as error:
                result.status = core.ScrapeStatus.ERROR
                result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
            else:
                if self.config.javascript:
                    resp.html.render(sleep=self.config.javascript_wait)
                if resp.status_code == 200:
                    result.status = core.ScrapeStatus.SUCCESS
                    timediff = datetime.datetime.now() - time
                    scrape_time = (timediff.total_seconds() * 1000 +
                                   timediff.microseconds / 1000)
                    result.add_scrape_page(resp.html.html,
                                           scrape_time=scrape_time,
                                           status=core.ScrapeStatus.SUCCESS)
                else:
                    result.status = core.ScrapeStatus.ERROR
                    result.error_msg = (
                        F'HTTP Error: {resp.status_code} - '
                        F'{http.HTTPStatus(resp.status_code).phrase}')

                next_url = resp.html.next()
                resp.close()

            if count >= self.config.max_pages:
                logger.debug(F'Paging limit of {self.config.max_pages} '
                            'reached, stop scraping')
                break

            if not self.config.attempt_multi_page:
                logger.debug((F'Multipage is not set, skip after first page'))
                break


        return result

    @classmethod
    def _validate_config(cls, config: core.ScrapeConfig) -> None:
        """Verify the config can be scraped by requests-html."""
        if config.wait_for_xpath:
            raise exceptions.ScrapeConfigError(
                "No Suport for Next pages via Xpath")
