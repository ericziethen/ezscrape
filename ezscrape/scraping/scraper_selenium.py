#!/usr/bin/env python3

"""Module to provie Scrape functionality using the selenium module."""

import contextlib
import datetime
import enum
import logging
import os

from dataclasses import dataclass
from typing import Dict, List, Tuple

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


@enum.unique
class WaitLogic(enum.Enum):
    """Enum to define the Wait Logic."""

    # pylint: disable=invalid-name
    MUST_HAVE = 'Must have'
    OPTIONAL = 'Optional'


@enum.unique
class WaitType(enum.Enum):
    """Enum to define the Wait Type."""

    # pylint: disable=invalid-name
    WAIT_FOR_CLICKABLE = 'Wait for Clickable'
    WAIT_FOR_LOCATED = 'Wait for Located'


@dataclass
class WaitCondition():
    locator: Tuple[By, str]
    wait_logic: WaitLogic = WaitLogic.MUST_HAVE
    wait_type: WaitType = WaitType.WAIT_FOR_LOCATED

    def id(self):
        """Provide the Id of this Element."""
        return str(self)


class ScraperWait():
    """Handle simple multiple conditions for waiting for Elements to Load."""

    def __init__(self, conditions: List[WaitCondition]):
        """Initialize the Waiter object."""
        # TODO - Maybe have setter to check Conditions are Valid (unique IDs?)
        self._conditions = conditions
        self.found_elements = {}
        self._found_might_have_count = 0
        self._found_must_have_count = 0

    def __call__(self, driver):
        # Test all outstanding events
        must_have_ok = True
        for cond in self._conditions:
            if cond.id() not in self.found_elements:
                elem = None
                if cond.wait_type == WaitType.WAIT_FOR_CLICKABLE:
                    elem = self._find_element(
                        driver, cond.locator, visible=True, enabled=True)
                elif cond.wait_type == WaitType.WAIT_FOR_LOCATED:
                    elem = self._find_element(driver, cond.locator)

                # If must have and not found we cannot complete yet
                if (elem is None) and (cond.wait_logic == WaitLogic.MUST_HAVE):
                    must_have_ok = False

                if elem is not None:
                    self.found_elements[cond.id()] = elem
                    if cond.wait_logic == WaitLogic.OPTIONAL:
                        self._found_might_have_count += 1
                    elif cond.wait_logic == WaitLogic.MUST_HAVE:
                        self._found_must_have_count += 1

        # Verify if we have everything we need
        # Our conditions are met if
        #   - all must_haves are met and at least 1 must_have in list
        #   - no must_haves defined and at least 1 might have found
        if must_have_ok:  # No issues with Must Haves (all good or none)
            if (self._found_must_have_count > 0) or\
               (self._found_might_have_count > 0):
                # We need to return an element, so pick any
                return list(self.found_elements.values())[0]

        # We haven't found an element fulfilling our conditions
        return False



    @staticmethod
    def _find_element(driver, locator, *,
                      visible: bool = False, enabled: bool = False):
        found_elem = None
        try:
            candidate_elem = EC._find_element(driver, locator)
        except NoSuchElementException:
            pass
        else:
            if (visible and not candidate_elem.is_displayed()) or\
               (enabled and not candidate_elem.is_enabled()):
                found_elem = None
            else:
                found_elem = candidate_elem

        return found_elem


# TODO - Can we write this as a normal Context Manager using __enter__?
# TODO - There might be a reason we picked this but we need to comment if not possible
@contextlib.contextmanager
def SeleniumChromeSession(*, config: core.ScrapeConfig = None):
    """Context Manager wrapper for a Selenium Chrome Session."""

    # TODO - WHat was the reason to not use a ContextManager with __enter__ ...???

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

    # TODO - Is that still valid now that we have separate proxy settings?
    proxy = ''
    if config is not None:
        if config.url.startswith('https'):
            proxy = config.proxy_https
        elif config.url.startswith('http'):
            proxy = config.proxy_http

    # TODO - Split the URL to get the correct schema
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument(F'user-agent={web_lib.random_useragent()}')
    if proxy:
        chrome_options.add_argument(F'--proxy-server={proxy}')

    # TODO - SELENIUM Might have some issue with Proxy Verification
    # See https://stackoverflow.com/questions/12848327/how-to-run-selenium-web-driver-behind-a-proxy-server-which-needs-authentication/35293284#35293284

    with webdriver.Chrome(
            chrome_options=chrome_options,
            executable_path=chrome_web_driver_path) as browser:
        print(F'BEFORE: {datetime.datetime.now()}')
        yield (browser)
        print(F'AFTER: {datetime.datetime.now()}')


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
        # TODO - WE SHOULD BE ABLE TO HANDLE EVERYTHING IN HERE
        if not config.xpath_next_button:
            raise exceptions.ScrapeConfigError(
                'Selenium needs and Xpath Element Specified')

    def _scrape_with_browser(self, browser=None) -> core.ScrapeResult:
        """Scrape using Selenium with Chrome."""
        # TODO - THIS PROBABLY NEEDS REFACTORING TO MAKE IT SIMPLER
        result = core.ScrapeResult(self.config.url)
        multi_page = self.config.attempt_multi_page
        count = 0

        try:
            browser.get(self.config.url)
        except WebDriverException as error:
            result.status = core.ScrapeStatus.ERROR
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        else:
            while True:
                count += 1
                # SOME PAGE LOAD INFO AND TIPS if there are issues
                # http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html

                # No Default Waiting Condition = wait for load timeout
                wait_conditions = []

                # Add a waiting Condition
                if self.config.xpath_next_button:
                    next_button_condition = browser.WaitCondition(
                        (By.XPATH, self.config.xpath_next_button),
                        WaitLogic.MUST_HAVE, WaitType.WAIT_FOR_CLICKABLE)
                    wait_conditions.append(next_button_condition)

                if self.config.xpath_wait_for_loaded:
                    wait_conditions.append(browser.WaitCondition(
                        (By.XPATH, self.config.xpath_next_button),
                        WaitLogic.MUST_HAVE, WaitType.WAIT_FOR_LOCATED))

                scraper_wait = ScraperWait(wait_conditions)

                time = datetime.datetime.now()
                try:
                    element = WebDriverWait(
                        browser, self.config.request_timeout).until(scraper_wait)
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

                    # If Next Button Found Press
                    if next_button_condition.id() in scraper_wait.found_elements:
                        scraper_wait.found_elements[next_button_condition.id()].click()
                    else:
                        break

        return result

