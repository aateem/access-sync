import yaml
from conftest import ORG, REPO_A, USER_LOGIN_A, USER_LOGIN_B

from access_manager.manifest import GitHubManifest


def test_manifest_create_team_and_add_member(gh_adapter, gh_org_cleanup):
    """Check that the manifest can create a team and add a member to it."""
    assert not gh_adapter.list_teams(ORG)

    manifest_content = f"""
organizations:
  - name: {ORG}
    teams:
      - name: test-team-one
        repos:
          - name: {REPO_A}
            owner: {ORG}
            permission: maintain
        members:
          - login: {USER_LOGIN_B}
            role: member
"""
    manifest = GitHubManifest(yaml.safe_load(manifest_content))
    manifest.apply()

    # check the team was created
    teams = gh_adapter.list_teams(ORG)
    assert len(teams) == 1
    assert teams[0]["name"] == "test-team-one"

    # check the added team member has the required role
    members = gh_adapter.list_team_memberships(ORG, teams[0]["slug"], role="member")
    assert len(members) == 1
    assert members[0]["login"] == USER_LOGIN_B

    # check team repositories
    repos = gh_adapter.list_team_repositories(ORG, teams[0]["slug"])
    assert len(repos) == 1
    assert repos[0]["name"] == REPO_A
    assert repos[0]["permissions"]["maintain"]


def test_manifest_delete_team_member(gh_adapter, gh_org_cleanup):
    """Check that the manifest can delete a team member."""
    assert not gh_adapter.list_teams(ORG)

    new_team = gh_adapter.add_team(ORG, "test-team-one")
    gh_adapter.add_team_membership(ORG, new_team["slug"], USER_LOGIN_B)

    new_team = gh_adapter.add_team(ORG, "test-team-two")
    gh_adapter.add_team_membership(ORG, new_team["slug"], USER_LOGIN_A)

    manifest_content = f"""
organizations:
  - name: {ORG}
    teams:
      - name: test-team-one
        members:
          - login: {USER_LOGIN_B}
            remove: true
          - login: {USER_LOGIN_A}
            role: member
      - name: test-team-two
        members:
          - login: {USER_LOGIN_B}
            role: member
          - login: {USER_LOGIN_A}
            remove: true
"""

    manifest = GitHubManifest(yaml.safe_load(manifest_content))
    manifest.apply()

    teams = gh_adapter.list_teams(ORG)
    assert len(teams) == 2

    teams = {team["name"]: team for team in teams}
    assert USER_LOGIN_B not in {
        member["login"] for member in gh_adapter.list_team_memberships(ORG, teams["test-team-one"]["slug"])
    }
    assert USER_LOGIN_A not in {
        member["login"] for member in gh_adapter.list_team_memberships(ORG, teams["test-team-two"]["slug"])
    }
