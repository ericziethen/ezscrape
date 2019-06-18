#!/usr/bin/env python3

"""Module to provie Scrape functionality using the selenium module."""

import contextlib
import datetime
import logging
import os

from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import scraping.core as core
import scraping.exceptions as exceptions
import scraping.web_lib as web_lib

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

CHROME_WEBDRIVER_ENV_VAR = 'CHROME_WEBDRIVER_PATH'


class SeleniumSetupError(Exception):
    """Exception is Selenium is not Setup Correctly."""


@contextlib.contextmanager
def SeleniumChromeSession(*, config: core.ScrapeConfig = None):
    """Context Manager wrapper for a Selenium Chrome Session."""
    # TODO - Support Chrome Portable Overwrite
        # String chromePath = "M:/my/googlechromeporatble.exe path"; 
        #   options.setBinary(chromepath);
        #   System.setProperty("webdriver.chrome.driver",chromedriverpath);
    #chrome_exec_var=

    # TODO - The Module will probably come with a default Chrome Webdriver
    # TODO - IFFFFFF Different Versions work with different Versions of Chrome and
    # TODO - then let the user overwrite it
    # TODO - Otherwise User needs to setup both somehow
    # TODO - ??? Config
    # TODO - ??? Env Variable
    # TODO - ??? Parameter
    # TODO - 
    chrome_web_driver_path = os.environ.get(CHROME_WEBDRIVER_ENV_VAR)
    if chrome_web_driver_path is None:
        raise SeleniumSetupError((F'Webdriver not found, set path as env '
                                  F'Variable: "{CHROME_WEBDRIVER_ENV_VAR}"'))

    proxy = ''
    if config is not None:
        if config.url.startswith('https'):
            proxy = config.proxy_https
        elif config.url.startswith('http'):
            proxy = config.proxy_http

    # TODO - Split the URL to get the correct schema
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument(F'user-agent={web_lib.generic_useragent()}')
    if proxy:
        chrome_options.add_argument(F'--proxy-server={proxy}')

    # TODO - SELENIUM Might have some issue with Proxy Verification
    # See https://stackoverflow.com/questions/12848327/how-to-run-selenium-web-driver-behind-a-proxy-server-which-needs-authentication/35293284#35293284

    with webdriver.Chrome(
            chrome_options=chrome_options,
            executable_path=chrome_web_driver_path) as browser:
        yield (browser)


class SeleniumChromeScraper(core.Scraper):
    """Implement the Scraper using requests."""
    def __init__(self, config: core.ScrapeConfig, *, browser=None):
        """Initialize the Selenium Scraper."""
        super().__init__(config)
        self.browser = browser

    def scrape(self) -> core.ScrapeResult:
        """Handle existing browser session or create a new one."""
        if self.browser is not None:
            result = self._scrape_with_browser(self.browser)
        else:
            with SeleniumChromeSession() as browser:
                result = self._scrape_with_browser(browser)
        return result

    @classmethod
    def _validate_config(cls, config: core.ScrapeConfig) -> None:
        """Verify the config can be scraped by requests."""
        # TODO - THIS NEEDS REFACTORING, WE SHOULD SUPPORT EXPLICIT WAIT AS WELL
        if not config.wait_for_xpath:
            raise exceptions.ScrapeConfigError(
                'Selenium needs and Xpath Element Specified')

    def _scrape_with_browser(self, browser=None) -> core.ScrapeResult:
        """Scrape using Selenium with Chrome."""
        # TODO - THIS PROBABLY NEEDS REFACTORING TO MAKE IT SIMPLER
        result = core.ScrapeResult(self.config.url)
        multi_page = self.config.attempt_multi_page
        xpath_bttn = self.config.wait_for_xpath
        count = 0

        try:
            r = browser.get(self.config.url)
        except WebDriverException as error:
            result.status = core.ScrapeStatus.ERROR
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        else:
            while True:
                count += 1
                # SOME PAGE LOAD INFO AND TIPS if there are issues
                # http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html

                try:
                    time = datetime.datetime.now()
                    # TODO - Can't remember why we are having 2 different ways
                    # TODO - Try to avoid using multi_page, but is there a case for both?
                    # TODO - Maybe have a Next Button Xpath and a Wait For Xpath?
                    # TODO - How to wait for both if we have both?
                    if multi_page:
                        element = WebDriverWait(
                            browser, self.config.request_timeout).until(
                                EC.element_to_be_clickable((By.XPATH, xpath_bttn)))
                    else:
                        element = WebDriverWait(
                            browser, self.config.request_timeout).until(
                                EC.presence_of_element_located((By.XPATH, xpath_bttn)))
                except TimeoutException as error:
                    result.status = core.ScrapeStatus.TIMEOUT
                    # TODO - Maybe this should be an error and success state for each sub page
                    #result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
                    timediff = datetime.datetime.now() - time
                    scrape_time = (timediff.total_seconds() * 1000 +
                                timediff.microseconds / 1000)
                    result.add_scrape_page(browser.page_source,
                                            scrape_time=scrape_time,
                                            status=core.ScrapeStatus.TIMEOUT)
                    result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
                    break
                else:
                    result.status = core.ScrapeStatus.SUCCESS
                    timediff = datetime.datetime.now() - time
                    scrape_time = (timediff.total_seconds() * 1000 +
                                    timediff.microseconds / 1000)
                    result.add_scrape_page(browser.page_source,
                                        scrape_time=scrape_time,
                                        status=core.ScrapeStatus.SUCCESS)

                    if count >= self.config.max_pages:
                        logger.debug(F'Paging limit of {self.config.max_pages} reached, stop scraping')
                        break

                    if multi_page:
                        # Click the next Button
                        element.click()
                    else:
                        break

        return result

