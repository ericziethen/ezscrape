import pytest

import scraping.web_lib as web_lib


def test_phrase_from_response_code():
    phrase = web_lib.phrase_from_response_code(200)
    assert phrase == 'OK'


def test_phrase_from_response_code_invalid_code():
    with pytest.raises(ValueError):
        web_lib.phrase_from_response_code(20000)


@pytest.mark.proxytest
def test_split_url():
    url = 'http://91.208.39.70:8080'
    url_split = web_lib.split_url(url)

    assert url_split.scheme == 'http'
    assert url_split.hostname == '91.208.39.70'
    assert url_split.port == 8080
