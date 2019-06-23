#!/usr/bin/env python3

"""Module to provie Scrape functionality using the selenium module."""

import contextlib
import datetime
import enum
import logging
import os

from dataclasses import dataclass
from typing import Dict, List, Tuple

from selenium.common.exceptions import (
    NoSuchElementException, StaleElementReferenceException, TimeoutException, WebDriverException)
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
        print(F'ScraperWait_init, conditions: {conditions}')
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
        print(F'_find_element(): Locator: {locator}, visible: {visible}, enabled: {enabled}')
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

    def _scrape_with_browser(self, browser=None) -> core.ScrapeResult:
        """Scrape using Selenium with Chrome."""
        # TODO - THIS PROBABLY NEEDS REFACTORING TO MAKE IT SIMPLER
        result = core.ScrapeResult(self.config.url)
        count = 0

        # No Default Waiting Condition = wait for load timeout
        wait_conditions = []

        # Add a waiting Condition
        next_button_condition = None
        if self.config.xpath_next_button:
            next_button_condition = WaitCondition(
                (By.XPATH, self.config.xpath_next_button),
                WaitLogic.MUST_HAVE, WaitType.WAIT_FOR_CLICKABLE)
            wait_conditions.append(next_button_condition)
        
        if self.config.xpath_wait_for_loaded:
            wait_conditions.append(WaitCondition(
                (By.XPATH, self.config.xpath_wait_for_loaded),
                WaitLogic.MUST_HAVE, WaitType.WAIT_FOR_LOCATED))

        if self.config.wait_for_page_load_seconds > 0:
            browser.set_page_load_timeout(self.config.wait_for_page_load_seconds)
            print(F'{datetime.datetime.now()} - set set_page_load_timeout to {self.config.wait_for_page_load_seconds}')
        
        try:
            print(F'{datetime.datetime.now()} - Start Get Url')
            browser.get(self.config.url)
            print(F'{datetime.datetime.now()} - Finish Get Url')
        except WebDriverException as error:
            print(F'{datetime.datetime.now()} - WebDriverException')
            result.status = core.ScrapeStatus.ERROR
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        else:
            while True:
                count += 1
                print(F'### Page Load Count: {count}')

                # Initialize the Scraper Wait object for each iteration / page,
                # because it stores found elements
                scraper_wait = ScraperWait(wait_conditions)

                # SOME PAGE LOAD INFO AND TIPS if there are issues
                # http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html

                try:
                    if wait_conditions:
                        print(F'{datetime.datetime.now()} - Start Explicit wait')
                        element = WebDriverWait(
                            browser, self.config.request_timeout).until(scraper_wait)
                        print(F'{datetime.datetime.now()} - Finish Explicit wait')
                    else:
                        print(F'{datetime.datetime.now()} - Skip Explicit wait, no Conditions')
                except TimeoutException as error:
                    print(F'{datetime.datetime.now()} - TimeoutException')
                    result.status = core.ScrapeStatus.TIMEOUT
                    # TODO - Maybe this should be an error and success state for each sub page
                    #result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
                    result.add_scrape_page(browser.page_source,
                                           status=core.ScrapeStatus.TIMEOUT)
                    result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
                    break
                else:
                    print(F'{datetime.datetime.now()} - OK else block')
                    result.status = core.ScrapeStatus.SUCCESS

                    print(F'Found Elements: {scraper_wait.found_elements}')

                    result.add_scrape_page(browser.page_source,
                                           status=core.ScrapeStatus.SUCCESS)
                    print(F'{datetime.datetime.now()} - Stored HTML')

                    if count >= self.config.max_pages:
                        logger.debug(F'Paging limit of {self.config.max_pages} reached, stop scraping')
                        break

                    # TODO - We're getting some staleness issues here
                    # TODO - See https://stackoverflow.com/questions/40029549/how-to-avoid-staleelementreferenceexception-in-selenium-python
                    # TODO - For Ideas
                    # If Next Button Found Press
                    if (next_button_condition is not None) and\
                       (next_button_condition.id() in scraper_wait.found_elements):
                    
                        next_elem = scraper_wait.found_elements[next_button_condition.id()]
                        

                        # TODO - We need to clear the found elements to search for them again
                        #scraper_wait.found_elements = {}

                        #browser.implicitly_wait(5)
                        print(F'Clicking Next Button: {next_elem}')
                        next_elem.click()

                        # TODO - Some Ideas:
                        # https://blog.codeship.com/get-selenium-to-wait-for-page-load/
                        #WebDriverWait(browser, 10).until(EC.staleness_of(next_elem))
                        #browser.wait.until(EC.staleness_of(next_elem))
                    else:
                        break

        return result


