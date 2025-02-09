from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any

from loguru import logger
from pydantic import BaseModel

from access_manager.adapter import Adapter, GitHubAdapter
from access_manager.models import github


class Manifest(ABC):
    validator: BaseModel
    adapter: Adapter

    def __init__(self, manifest_data: Any):
        self.manifest = self.validator.model_validate(manifest_data)

    @abstractmethod
    def apply(self):
        # TODO: this is a template for future integrations (JIra, etc.)
        # the current vision is that the apply's logic might be to diverse to
        # be implemented in the base class
        raise NotImplementedError


class GitHubManifest(Manifest):
    validator = github.Organizations

    def __init__(self, manifest_data: Any):
        super().__init__(manifest_data)
        self.local = {}

    @cached_property
    def adapter(self) -> GitHubAdapter:
        return GitHubAdapter()

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
