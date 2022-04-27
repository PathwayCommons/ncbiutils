import pytest

import responses
from requests import ConnectionError, HTTPError, Timeout
from ncbiutils.http import safe_requests, RequestsError

TEST_URL = 'https://fakedomain.org/'

@responses.activate
@pytest.mark.parametrize('status', [200, 204, 302])
def test_no_error_on_status_ok(status):
    responses.add(
        responses.GET,
        TEST_URL,
        status = status
    )
    error, _ = safe_requests(TEST_URL)
    assert error is None, f'Error on good status {status}'


@responses.activate
@pytest.mark.parametrize('status', [400, 404, 500])
def test_error_on_bad_status(status):
    responses.add(
        responses.GET,
        TEST_URL,
        body = RequestsError(status),
        status = status
    )
    error, _ = safe_requests(TEST_URL)
    assert error is not None, f'No error on bad status {status}'
    assert isinstance(error, RequestsError), f'Wrong error type'


@responses.activate
@pytest.mark.parametrize('body', [ConnectionError, HTTPError, Timeout])
def test_error_on_exception(body):
    responses.add(
        responses.GET,
        TEST_URL,
        body = body
    )
    error, _ = safe_requests(TEST_URL)
    assert error is not None, f'No error on Exception'
    assert isinstance(error, Exception), f'Wrong error type'
