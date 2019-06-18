#!/usr/bin/env python3

"""Module providing misc web related functionality."""

import http
import urllib.parse

from collections import namedtuple

import fake_useragent


def random_useragent() -> str:
    """Generate a generic user agent."""
    return fake_useragent.UserAgent().random


def phrase_from_response_code(code: int) -> str:
    """Get a Response phjrase from an error code."""
    # Pylint has an issue with this call even though correct
    # pylint: disable=no-value-for-parameter
    status_code = http.HTTPStatus(code)
    # pylint: enable=no-value-for-parameter

    return status_code.phrase


def split_url(url: str):
    """Split the url into it's components."""
    url_split = namedtuple('url_split', ['scheme', 'hostname', 'port'])
    result = urllib.parse.urlparse(url)
    return url_split(result.scheme, result.hostname, result.port)
