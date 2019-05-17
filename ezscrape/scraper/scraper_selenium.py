#!/usr/bin/env python3

"""Module to provie Scrape functionality using the selenium module."""

import contextlib
import datetime
import logging
import os

from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import scraper.core as core
import scraper.exceptions as exceptions

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

CHROME_WEBDRIVER_ENV_VAR = 'CHROME_WEBDRIVER_PATH'


class SeleniumSetupError(Exception):
    """Exception is Selenium is not Setup Correctly."""


@contextlib.contextmanager
def SeleniumChromeSession():
    """Context Manager wrapper for a Selenium Chrome Session."""
    # TODO - Support Chrome Portable Overwrite
        # String chromePath = "M:/my/googlechromeporatble.exe path"; 
        #   options.setBinary(chromepath);
        #   System.setProperty("webdriver.chrome.driver",chromedriverpath);
    #chrome_exec_var=

    chrome_web_driver_path = os.environ.get(CHROME_WEBDRIVER_ENV_VAR)
    if chrome_web_driver_path is None:
        raise SeleniumSetupError((F'Webdriver not found, set path as env '
                                  F'Variable: "{CHROME_WEBDRIVER_ENV_VAR}"'))

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')

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


    def _scrape_with_browser(self, browser=None) -> core.ScrapeResult:
        """Scrape using Selenium with Chrome."""
        # TODO - THIS PROBABLY NEEDS REFACTORING TO MAKE IT SIMPLER
        
        result = core.ScrapeResult(self.config.url)
        xpath_bttn = self.config.next_page_button_xpath
        if xpath_bttn:
            count = 0
            r = browser.get(self.config.url)
            while True:
                count += 1
                # SOME PAGE LOAD INFO AND TIPS if there are issues
                # http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html

                try:
                    time = datetime.datetime.now()
                    element = WebDriverWait(
                        browser, self.config.request_timeout).until(
                            EC.element_to_be_clickable((By.XPATH, xpath_bttn)))
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

                    # Click the next Button
                    element.click()
        else:
            result.status = core.ScrapeStatus.SUCCESS
            time = datetime.datetime.now()
            # TODO - If Javascript Page need to Wait, or Wait by default a bit longer
            # TODO - SELENIUM might not need to know if it's javascript and just use a default wait time
            # TODO - We might need an implicit wait here
            r = browser.get(self.config.url)
            timediff = datetime.datetime.now() - time
            scrape_time = (timediff.total_seconds() * 1000 +
                           timediff.microseconds / 1000)
            result.add_scrape_page(browser.page_source,
                                scrape_time=scrape_time,
                                status=core.ScrapeStatus.SUCCESS)
        return result
