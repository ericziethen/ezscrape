#!/usr/bin/env python3

"""Module providing misc web related functionality."""

import http

import fake_useragent


# TODO - Check fake-useragent, can specify a list for rotation
def generic_useragent() -> str:
    """Generate a generic user agent."""
    return fake_useragent.UserAgent().chrome


def phrase_from_response_code(code: int) -> str:
    """Get a Response phjrase from an error code."""
    # Pylint has an issue with this call even though correct
    # pylint: disable=no-value-for-parameter
    status_code = http.HTTPStatus(code)
    # pylint: enable=no-value-for-parameter

    return status_code.phrase
