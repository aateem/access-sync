import pytest
from loguru import logger

from main import GitHubAdapter

ORG = "aateem-org"


@pytest.fixture
def ensure_cleanup():
    yield
    adapter = GitHubAdapter()
    teams = adapter.list_teams(ORG)
    for team in teams:
        logger.info(f"Removing team {team['slug']}")
        adapter.remove_team(ORG, team["slug"])


def test_add_team(ensure_cleanup):
    adapter = GitHubAdapter()
    name = "test"
    new_team = adapter.add_team(ORG, name, "test team", "closed", "mention")
    teams = adapter.list_teams(ORG)
    for team in teams:
        if team["name"] == name:
            assert team["id"] == new_team["id"]
            assert team["name"] == name
            assert team["slug"] == name
            break
    adapter.remove_team(ORG, team["slug"])
    teams = adapter.list_teams(ORG)
    assert not any(team["name"] == name for team in teams)
