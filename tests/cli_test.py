from conftest import ORG, REPO_A, REPO_B, USER_LOGIN_A, USER_LOGIN_B
from typer.testing import CliRunner

from access_manager.cli import cli


def test_list_memberships(gh_org_cleanup):
    runner = CliRunner()
    result = runner.invoke(cli, ["gh", "list-memberships", ORG])
    assert result.exit_code == 0
    assert all(user in result.stdout for user in [USER_LOGIN_A, USER_LOGIN_B])


def test_add_team_with_repos(gh_org_cleanup):
    runner = CliRunner()
    result = runner.invoke(
        cli, ["gh", "add-team", ORG, "test-team", "--repo-names", f"{ORG}/{REPO_A}", "--repo-names", f"{ORG}/{REPO_B}"]
    )
    assert result.exit_code == 0
    assert "'repos_count': 2" in result.stdout
