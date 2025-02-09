import yaml

from access_manager.manifest import GitHubManifest


def test_manifest_create_team_and_add_member(gh_adapter, gh_org_cleanup):
    assert not gh_adapter.list_teams("aateem-org")

    manifest_content = """
organizations:
  - name: aateem-org
    teams:
      - name: test-team-one
        repos:
          - name: test
            owner: aateem-org
            permission: maintain
        members:
          - login: reluctant-participant
            role: member
"""
    manifest = GitHubManifest(yaml.safe_load(manifest_content))
    manifest.apply()

    # check the team was created
    teams = gh_adapter.list_teams("aateem-org")
    assert len(teams) == 1
    assert teams[0]["name"] == "test-team-one"

    # check team repositories
    repos = gh_adapter.list_team_repositories("aateem-org", teams[0]["slug"])
    assert len(repos) == 1
    assert repos[0]["name"] == "test"
    assert repos[0]["permissions"]["maintain"]
