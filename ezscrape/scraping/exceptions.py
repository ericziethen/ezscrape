#!/usr/bin/env python3

"""Provide Exceptions for Scraping Functionality."""


class ScrapeError(Exception):
    """Generic Page Scrape Error."""


class ScrapeConfigError(ScrapeError):
    """Error with the Scrape Config."""
