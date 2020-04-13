#!/usr/bin/env python3

"""Module providing misc web related functionality."""

import http
import urllib.parse

from dataclasses import dataclass

import fake_useragent


@dataclass
class UrlSplit:
    """Class representing a Split Url."""

    scheme: str
    hostname: str
    port: int


def random_useragent() -> str:
    """Generate a generic user agent."""
    return fake_useragent.UserAgent().random  # type: ignore


def phrase_from_response_code(code: int) -> str:
    """Get a Response phjrase from an error code."""
    # Pylint has an issue with this call even though correct
    # pylint: disable=no-value-for-parameter
    status_code = http.HTTPStatus(code)
    # pylint: enable=no-value-for-parameter

    return status_code.phrase  # pylint: disable=no-member


def split_url(url: str) -> UrlSplit:
    """Split the url into it's components."""
    result = urllib.parse.urlparse(url)
    return UrlSplit(scheme=result.scheme,
                    hostname=result.hostname,  # type: ignore
                    port=result.port)  # type: ignore
