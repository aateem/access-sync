from typing import Any, List, Literal

from loguru import logger
from pydantic import BaseModel

from access_manager.adapter import GitHubAdapter


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
    name: str


class Organization(BaseModel):
    name: str
    teams: List[Team]


class Organizations(BaseModel):
    organizations: List[Organization]


class GitHubManifest:
    def __init__(self, manifest_data: Any, github_adapter: GitHubAdapter):
        self.manifest = Organizations.model_validate(manifest_data)
        self.adapter = github_adapter
        self.local = {}

    def apply(self):
        logger.info("Applying manifest")
        for org in self.manifest.organizations:
            self.local[org.name] = {team["name"]: team for team in self.adapter.list_teams(org.name)}

            for team in org.teams:
                if team.name not in self.local[org.name]:
                    logger.info(f"Adding new team {team.name}")
                    new_team = self.adapter.add_team(org.name, team.name)
                    self.local[org.name][team.name] = new_team

                team_slug = self.local[org.name][team.name]["slug"]

                for repo in team.repos:
                    logger.info(f"Updating repository {repo.name} access")
                    self.adapter.add_team_repository_permissions(
                        org.name, team_slug, repo.name, repo.owner, repo.permission
                    )

                for member in team.members:
                    if member.remove:
                        logger.info(f"Removing {member.login} from team {team.name}")
                        self.adapter.remove_team_membership(org.name, team_slug, member.login)
                    else:
                        logger.info(f"Adding {member.login} to team {team.name} with role {member.role}")
                        self.adapter.add_team_membership(org.name, team_slug, member.login, member.role)

        logger.debug(f"applied manifest: {self.manifest.model_dump()}")
