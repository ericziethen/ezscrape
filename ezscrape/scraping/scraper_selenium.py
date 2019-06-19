#!/usr/bin/env python3

"""Module to provie Scrape functionality using the selenium module."""

import contextlib
import datetime
import enum
import logging
import os

from dataclasses import dataclass
from typing import List, Tuple

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




# TODO - IMPLEMENT
# TODO - Design a Solution based on the following recommodations
# Some Ideas @ https://github.com/SeleniumHQ/selenium/issues/7121
# TODO - Hava a Mechanism where we can
# TODO      - Define Multiple Wait Conditions
# TODO      - Support And/Or
# TODO      - Hanldle if Nothing Specified (ignore)
# TODO      - Add Function vs __init__ setting???
# !!!       How to handle with Different Waiting Events like
#               - Wait for Element
#               - Wait Until Clickable
''' 
    class expected_or(object):
        """ perform a logical 'OR' check on multiple expected conditions """
        def __init__(self, *args):
            self.expected_conditions = args

        def __call__(self, driver):
            for expected_condition in self.expected_conditions:
                try:
                    result = expected_condition(driver)
                    if result:
                        return result
                except NoSuchElementException:
                    pass

  IDEAS
  - No Conditions (if allowed)
  - elements that must be found (and-ish)
  - elements that might be there (or-ish)
  - store elements in dictionary as result (Default Dict as None???)

    -> This gives us a basic and/or
  - But What about more Complex
    -> (A and B) OR (C and D)
        -> Could have Sub Condition Class and 1 Handler of Condition
        -> Possible but more complex
        -> Class Condition
        -> Class Waiter
            -> Has Multiple Conditions
        -> For our case that might be too complicated now as nested conditions
           is not a simple issue
'''

@enum.unique
class WaitLogic(enum.Enum):
    """Enum to define the Wait Logic."""

    # pylint: disable=invalid-name
    MUST_HAVE = 'Must have'
    MIGHT_HAVE = 'Might have'


@enum.unique
class WaitType(enum.Enum):
    """Enum to define the Wait Type."""

    # pylint: disable=invalid-name
    WAIT_FOR_CLICKABLE = 'Wait for Clickable'
    WAIT_FOR_LOCATED = 'Wait for Located'


@dataclass
class WaitCondition():
    locator: Tuple[By, str]
    wait_type: WaitType
    wait_logic: WaitLogic


class ScraperWait():
    """Handle simple multiple conditions for waiting for Elements to Load."""

    def __init__(self, conditions: List[WaitCondition]):
        """Initialize the Waiter object."""
        self._must_have_list: List[WaitCondition] = []
        self._might_have_list: List[WaitCondition] = []

        # Separate the conditions
        for cond in conditions:
            if cond.wait_type == WaitLogic.MUST_HAVE:
                self._must_have_list.append(cond)
            elif cond.wait_type == WaitLogic.MIGHT_HAVE:
                self._might_have_list.append(cond)
            else:
                raise ValueError(F'Unexpected Wait Type: {cond.wait_type}')

    def __call__(self, driver):
        # Handle 
        driver.find_element???
        how to do clickable and locatable
        EC.element_to_be_clickable
        EC.presence_of_element_located

    def _wait_for_clickable(self):



    def _wait_for_locatable(self):










# TODO - Can we write this as a normal Context Manager using __enter__
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
            browser.get(self.config.url)
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
                    
                    # TODO - Design a Solution based on the following recommodations
                    # Some Ideas @ https://github.com/SeleniumHQ/selenium/issues/7121
                    # TODO - Hava a Mechanism where we can
                    # TODO      - Define Multiple Wait Conditions
                    # TODO      - Support And/Or
                    # TODO      - Hanldle if Nothing Specified (ignore)
                    # TODO      - Add Function vs __init__ setting???





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

