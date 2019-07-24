#!/usr/bin/env python3

"""Module to provie Scrape functionality using the selenium module."""

import enum
import logging
import os

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.support.ui import WebDriverWait

import ezscrape.scraping.core as core
import ezscrape.scraping.web_lib as web_lib

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


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
    """Define a Wait Condition."""

    locator: Tuple[By, str]
    wait_logic: WaitLogic = WaitLogic.MUST_HAVE
    wait_type: WaitType = WaitType.WAIT_FOR_LOCATED

    @property
    def key(self) -> str:
        """Provide the Id of this Element."""
        return str(self)


class ScraperWait():
    """Handle simple multiple conditions for waiting for Elements to Load."""

    # pylint: disable=too-few-public-methods

    def __init__(self, conditions: List[WaitCondition]):
        """Initialize the Waiter object."""
        self._conditions = conditions
        self.found_elements: Dict[str, WebElement] = {}
        self._found_might_have_count = 0
        self._found_must_have_count = 0

    def __call__(self, driver: RemoteWebDriver) -> Union[bool, WebElement]:
        """Handle Object Calls."""
        # Test all outstanding events
        must_have_ok = True
        for cond in self._conditions:
            if cond.key not in self.found_elements:
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
                    self.found_elements[cond.key] = elem
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
    def _find_element(driver: RemoteWebDriver,
                      locator: Tuple[By, str],
                      *,
                      visible: bool = False,
                      enabled: bool = False) -> WebElement:
        found_elem = None
        try:
            candidate_elem = driver.find_element(locator[0], locator[1])
        except NoSuchElementException:
            pass
        else:
            if (visible and not candidate_elem.is_displayed()) or\
               (enabled and not candidate_elem.is_enabled()):
                found_elem = None
            else:
                found_elem = candidate_elem

        return found_elem


class SeleniumChromeSession():
    """Context Manager wrapper for a Selenium Chrome Session."""

    chrome_webdriver_env_var = 'CHROME_WEBDRIVER_PATH'
    chrome_exec_env_var = 'CHROME_EXEC_PATH'

    def __init__(self, *, config: Optional[core.ScrapeConfig] = None):
        """Initialize the Session."""
        # Using Portable Chrome, we see some issues
        #   "DevToolsActivePort file doesn't exist"
        # raised from selenium sometimes, not always for the same tests
        self._chrome_path = os.environ.get(self.chrome_exec_env_var)
        if self._chrome_path is None:
            raise SeleniumSetupError((
                F'Chrome not found, set path as env Variable: '
                F'"{self.chrome_exec_env_var}"'))

        self._chrome_web_driver_path = os.environ.get(
            self.chrome_webdriver_env_var)
        if self._chrome_web_driver_path is None:
            raise SeleniumSetupError(
                (F'Webdriver not found, set path as env '
                 F'Variable: "{self.chrome_webdriver_env_var}"'))

        proxy = ''
        if config is not None:
            if config.url.startswith('https'):
                proxy = config.proxy_https
            elif config.url.startswith('http'):
                proxy = config.proxy_http

        self._chrome_options = webdriver.ChromeOptions()
        self._chrome_options.add_argument('--headless')
        self._chrome_options.add_argument('--no-sandbox')
        self._chrome_options.add_argument(
            F'user-agent={web_lib.random_useragent()}')
        if self._chrome_path is not None:
            self._chrome_options.binary_location = self._chrome_path

        # Disable Listening STDOUT message
        # https://bugs.chromium.org/p/chromedriver/issues/detail?id=2907#c3
        self._chrome_options.add_experimental_option(
            'excludeSwitches', ['enable-logging'])

        if proxy:
            self._chrome_options.add_argument(F'--proxy-server={proxy}')

        self._driver = webdriver.Chrome(
            chrome_options=self._chrome_options,
            executable_path=self._chrome_web_driver_path)

    def __enter__(self) -> RemoteWebDriver:
        return self._driver.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        self._driver.__exit__(exc_type, exc_val, exc_tb)


class SeleniumChromeScraper(core.Scraper):
    """Implement the Scraper using requests."""

    def __init__(self, config: core.ScrapeConfig, *,
                 driver: webdriver.Chrome = None):
        """Initialize the Selenium Scraper."""
        super().__init__(config)
        self.driver = driver

    def scrape(self) -> core.ScrapeResult:
        """Handle existing driver session or create a new one."""
        if self.driver is not None:
            result = self._scrape_with_driver(self.driver)
        else:
            with SeleniumChromeSession() as driver:
                result = self._scrape_with_driver(driver)
        return result

    def _scrape_with_driver(
            self, driver: webdriver.Chrome = None) -> core.ScrapeResult:
        """Scrape using Selenium with Chrome."""
        result = core.ScrapeResult(self.config.url)
        count = 0

        # No Default Waiting Condition = wait for load timeout
        wait_conditions = []

        # Add Next Button
        next_button_condition = None
        next_bttn = self.config.next_button
        if next_bttn is not None:
            next_button_condition = WaitCondition(
                (get_by_type_from_page_wait_element(
                    next_bttn.wait_type), next_bttn.wait_text),
                WaitLogic.MUST_HAVE, WaitType.WAIT_FOR_CLICKABLE)
            wait_conditions.append(next_button_condition)

        # Add Generic Wait Conditions
        for wait_elem in self.config.wait_for_elem_list:
            condition = WaitCondition(
                (get_by_type_from_page_wait_element(
                    wait_elem.wait_type), wait_elem.wait_text),
                WaitLogic.MUST_HAVE, WaitType.WAIT_FOR_LOCATED)
            wait_conditions.append(condition)

        if self.config.page_load_wait > 0:
            driver.set_page_load_timeout(self.config.page_load_wait)

        try:
            driver.get(self.config.url)
        except WebDriverException as error:
            result.status = core.ScrapeStatus.ERROR
            result.error_msg = F'EXCEPTION: {type(error).__name__} - {error}'
        else:
            while True:
                count += 1

                # Initialize the Scraper Wait object for each iteration / page,
                # because it stores found elements
                scraper_wait = ScraperWait(wait_conditions)

                # SOME PAGE LOAD INFO AND TIPS if there are issues
                # http://www.obeythetestinggoat.com/how-to-get-selenium-to-wait-for-page-load-after-a-click.html

                try:
                    if wait_conditions:
                        WebDriverWait(
                            driver,
                            self.config.request_timeout).until(scraper_wait)
                except TimeoutException as error:
                    result.status = core.ScrapeStatus.TIMEOUT
                    result.add_scrape_page(driver.page_source,
                                           status=core.ScrapeStatus.TIMEOUT)
                    result.error_msg =\
                        F'EXCEPTION: {type(error).__name__} - {error}'
                    break
                else:
                    result.status = core.ScrapeStatus.SUCCESS

                    result.add_scrape_page(driver.page_source,
                                           status=core.ScrapeStatus.SUCCESS)

                    if count >= self.config.max_pages:
                        logger.debug(F'Paging limit of {self.config.max_pages}'
                                     'reached, stop scraping')
                        break

                    # If Next Button Found Press
                    if ((next_button_condition is not None) and
                            (next_button_condition.key in
                             scraper_wait.found_elements)):
                        next_elem = scraper_wait.found_elements[
                            next_button_condition.key]

                        next_elem.click()
                    else:
                        break

        return result


def get_by_type_from_page_wait_element(
        wait_element: core.WaitForPageType) -> By:
    """Convert WaitForPageType to Selenium By Type."""
    if wait_element == core.WaitForPageType.XPATH:
        return By.XPATH

    raise ValueError(F'Wait Element "{wait_element}" not supported')
