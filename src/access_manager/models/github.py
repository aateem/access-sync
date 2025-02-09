from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Member(BaseModel):
    login: str
    role: Literal["member", "maintainer"] = "member"
    remove: bool = False


class Repo(BaseModel):
    name: str
    owner: str
    permission: Literal["pull", "triage", "push", "maintain", "admin"] = "pull"


class Team(BaseModel):
    members: Optional[List[Member]] = Field(default_factory=list)
    repos: Optional[List[Repo]] = Field(default_factory=list)
    name: str
    remove: bool = False


class Organization(BaseModel):
    name: str
    teams: List[Team]


class Organizations(BaseModel):
    organizations: List[Organization]
