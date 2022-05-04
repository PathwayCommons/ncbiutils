import requests  # type: ignore
from loguru import logger


class RequestsError(Exception):
    """Exception to signal when a request is not OK

    Attributes
    ----------
    status : int
        Integer Code of responded HTTP Status, e.g. 404.
    """

    def __init__(self, status, message='Request status is not OK'):
        self.status = status
        self.message = message
        super().__init__(self.message)


def safe_requests(url, method='GET', headers={}, timeout=5, **opts):
    """Wraps requests to handle bad HTTP status, exceptions"""
    error = None
    response = None
    try:
        r = requests.request(method, url, headers=headers, timeout=timeout, **opts)
    except Exception as e:
        logger.error(f'Error encountered in request to {url}: {e}')
        error = e
    else:
        if not r.ok:
            error = RequestsError(r.status_code)
        response = r
    finally:
        return (error, response)
