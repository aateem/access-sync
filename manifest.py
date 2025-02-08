from functools import cached_property
from pathlib import Path
from typing import List, Literal

import yaml
from pydantic import BaseModel

from main import GitHubAdapter


class Member(BaseModel):
    login: str
    role: Literal["member", "maintainer"] = "member"
    remove: bool = False


class Repo(BaseModel):
    name: str
    owner: str
    permission: Literal["pull", "triage", "push", "maintain", "admin"] = "pull"


class Team(BaseModel):
    members: List[Member]
    repos: List[Repo]


class Organization(BaseModel):
    name: str
    teams: List[Team]


class Organizations(BaseModel):
    organizations: List[Organization]


class GitHubManifest:
    def __init__(self, file_path: Path, github_adapter: GitHubAdapter):
        self.file_path = file_path
        self.adapter = github_adapter

    @cached_property
    def manifest(self):
        with open(self.file_path, "r") as file:
            return Organizations.model_validate(yaml.safe_load(file))

    def apply_manifest(self):
        for org in self.manifest.organizations:
            for team in org.teams:
                new_team = self.adapter.add_team(org.name, team.name)
                for repo in team.repositories:
                    self.adapter.add_team_repository_permissions(
                        org.name, new_team["slug"], repo.name, repo.owner, repo.permission
                    )
                for member in team.members:
                    if member.remove:
                        self.adapter.remove_team_membership(org.name, new_team["slug"], member.login)
                    else:
                        self.adapter.add_team_membership(org.name, new_team["slug"], member.login, member.role)
