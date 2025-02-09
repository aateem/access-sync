from abc import ABC
from functools import cached_property
from typing import Optional

from pydantic_settings import BaseSettings

from access_manager.client import HTTPClient


class Settings(BaseSettings):
    bearer_token: str


class Adapter(ABC):
    settings: BaseSettings
    http_client: HTTPClient

    # NOTE: for the extension to, say Jira project/team management, the operations set
    # should be unified; this is the improvement for the future


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

    def list_memberships(self, org: str):
        return self.http_client.get(f"/orgs/{org}/members")

    def list_teams(self, org: str):
        return self.http_client.get(f"/orgs/{org}/teams")

    def list_team_memberships(self, org: str, team_slug: str):
        return self.http_client.get(f"/orgs/{org}/teams/{team_slug}/members")

    def list_team_repositories(self, org: str, team_slug: str):
        return self.http_client.get(f"/orgs/{org}/teams/{team_slug}/repos")

    def add_team_repository_permissions(
        self, org: str, team_slug: str, repo: str, owner: str, permission: Optional[str] = "pull"
    ):
        return self.http_client.put(
            f"/orgs/{org}/teams/{team_slug}/repos/{owner}/{repo}", json={"permission": permission}
        )

    def add_team_membership(self, org: str, team_slug: str, username: str, role: Optional[str] = "member"):
        return self.http_client.put(f"/orgs/{org}/teams/{team_slug}/memberships/{username}", json={"role": role})

    def add_team(
        self,
        org: str,
        name: str,
        description: Optional[str] = "",
        privacy: Optional[str] = "closed",
        repo_names: Optional[list[str]] = None,
    ):
        body = {"name": name, "description": description, "privacy": privacy}
        if repo_names:
            body["repo_names"] = repo_names

        return self.http_client.post(
            f"/orgs/{org}/teams",
            json=body,
        )

    def remove_team_membership(self, org: str, team_slug: str, username: str):
        return self.http_client.delete(f"/orgs/{org}/teams/{team_slug}/memberships/{username}")

    def remove_team(self, org: str, team_slug: str):
        return self.http_client.delete(f"/orgs/{org}/teams/{team_slug}")
