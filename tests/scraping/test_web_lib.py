import pytest

import scraping.web_lib as web_lib


def test_generic_useragent():
    agent = web_lib.generic_useragent()
    # Not a perfect test, but for now should do
    assert agent.startswith('Mozilla/5.0')


def test_phrase_from_response_code():
    phrase = web_lib.phrase_from_response_code(200)
    assert phrase == 'OK'


def test_phrase_from_response_code_invalid_code():
    with pytest.raises(ValueError):
        web_lib.phrase_from_response_code(20000)
