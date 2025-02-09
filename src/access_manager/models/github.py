from typing import List, Literal

from pydantic import BaseModel


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
