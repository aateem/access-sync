import pytest
from loguru import logger

from access_manager.adapter import GitHubAdapter

ORG = "aateem-org"


@pytest.fixture
def gh_org_cleanup():
    # NOTE: since we only operate on the teams' access basis,
    # removing all the teams is enough to clean up the state of the test org
    yield
    adapter = GitHubAdapter()
    teams = adapter.list_teams(ORG)
    for team in teams:
        logger.info(f"Removing team {team['slug']}")
        adapter.remove_team(ORG, team["slug"])


@pytest.fixture(scope="session")
def gh_adapter():
    return GitHubAdapter()
