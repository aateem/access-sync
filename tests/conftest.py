import pytest
from loguru import logger

from access_manager.adapter import GitHubAdapter

# the following are values from the existing GH test org
ORG = "aateem-org"
USER_LOGIN_A = "aateem"
USER_LOGIN_B = "reluctant-participant"
REPO_A = "test"
REPO_B = "reluctant_test"


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
