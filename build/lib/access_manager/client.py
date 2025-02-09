from typing import Optional

import httpx
from loguru import logger
from tenacity import (
    RetryError,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class HTTPClient:
    def __init__(self, base_url: str, max_retries: int = 3, timeout: int = 10, headers: Optional[dict] = None):
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        headers = headers or {}
        self.client = httpx.Client(base_url=self.base_url, timeout=self.timeout, headers=headers)

    def retriable_request(
        self,
        method,
        endpoint,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ):
        try:
            for attempt in Retrying(
                stop=stop_after_attempt(self.max_retries),
                wait=wait_exponential(multiplier=1, min=1, max=10),
                retry=retry_if_exception_type(httpx.TimeoutException),
            ):
                with attempt:
                    response = self.client.send(
                        self.client.build_request(method, endpoint, params=params, headers=headers, json=json)
                    )
                    try:
                        response.raise_for_status()
                    except httpx.HTTPStatusError as e:
                        logger.error(f"Failed to make request to {endpoint}: {e}")
                    if response.status_code == httpx.codes.NO_CONTENT:
                        return {}
                    return response.json()
        except RetryError:
            pass

    def get(self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None):
        return self.retriable_request("GET", endpoint, params=params)

    def post(
        self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None, json: Optional[dict] = None
    ):
        return self.retriable_request("POST", endpoint, params=params, json=json)

    def put(
        self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None, json: Optional[dict] = None
    ):
        return self.retriable_request("PUT", endpoint, params=params, json=json)

    def delete(self, endpoint: str, params: Optional[dict] = None, headers: Optional[dict] = None):
        return self.retriable_request("DELETE", endpoint, params=params)

    def close(self):
        self.client.close()
