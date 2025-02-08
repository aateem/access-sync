import logging
from functools import cached_property
from typing import Optional

import httpx
from loguru import logger
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from tenacity import (
    RetryError,
    Retrying,
    after_log,
    before_log,
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
                before=before_log(logger, logging.DEBUG),
                after=after_log(logger, logging.DEBUG),
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


class Settings(BaseSettings):
    bearer_token: str


class GitHubManifest(BaseModel): ...


class GitHubAdapter:
    def __init__(self):
        self.settings = Settings()

    @cached_property
    def http_client(self) -> HTTPClient:
        return HTTPClient(
            base_url="https://api.github.com",
            headers={
                "Authorization": f"Bearer {self.settings.bearer_token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    def list_teams(self, org: str):
        return self.http_client.get(f"/orgs/{org}/teams")

    def list_team_members(self, org: str, team_slug: str):
        return self.http_client.get(f"/orgs/{org}/teams/{team_slug}/members")

    def add_team_member(self, org: str, team_slug: str, username: str, role: str):
        return self.http_client.put(f"/orgs/{org}/teams/{team_slug}/memberships/{username}", json={"role": role})

    def add_team(self, org: str, name: str, description: str, privacy: str, notification: str):
        return self.http_client.post(
            f"/orgs/{org}/teams",
            json={"name": name, "description": description, "privacy": privacy, "notification": notification},
        )

    def remove_team_member(self, org: str, team_slug: str, username: str):
        return self.http_client.delete(f"/orgs/{org}/teams/{team_slug}/memberships/{username}")

    def remove_team(self, org: str, team_slug: str):
        return self.http_client.delete(f"/orgs/{org}/teams/{team_slug}")
