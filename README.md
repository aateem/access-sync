[![Run functional tests](https://github.com/aateem/access-sync/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/aateem/access-sync/actions/workflows/python-app.yml)
[![Docker Image build](https://github.com/aateem/access-sync/actions/workflows/docker-image.yml/badge.svg)](https://github.com/aateem/access-sync/actions/workflows/docker-image.yml)

# Access Manager

## Overview
This project provides simplified automation for organization access policy management. Operating via concepts of `organizations`, `teams`, `repositories` and `team-members`.

Currently only GitHub adapter is supported which opperates on the assumption of exsing organizations and repositories (i.e. the automation would not create orgs, setup repos or invite external users to existing orgs).

The project provides cli interface for both "fine grained" resource management and "bulk" manifest update.

## Installation

### Prerequisites
- Python >= 3.12

### Setup
Install as a Python package
```bash
python -m venv venv
pip install -U pip
pip install .
pip install ".[test]"
```

Build docker image
```bash
docker build access-manager-cli .
```

## Usage

Requires GitHub Access Token provided as `BEARER_TOKEN` env var.

### As CLI
```bash
am --help
```
The adapters (currently GitHub only) are exposed as subcommands

### Manifest apply
```yaml
organizations:
  - name: org-name
    teams:
      - name: team-to-create-update
        repos:
          - name: repo-name
            owner: repo-owner
            permission: maintain
        members:
          - login: new-team-member-login
            role: member
```
Aply via:
```bash
am gh apply-manifest <path to the file above>
```

### As a lib
```python
from access_manager.adapter import GitHubAdapter
adapter = GitHubAdapter()
    teams = adapter.list_teams('some-org')
    for team in teams:
        logger.info(f"Removing team {team['slug']}")
        adapter.remove_team('some-org', team["slug"])

from access_manager.manifest import GitHubManifest
manifest = GitHubManifest(yaml.safe_load(manifest_content))
manifest.apply()
```

## Architecture

Subject to change

![alt text](arch_diagram.png)

## Areas of improvements

- Add other adapters/manifest processors, e.g. Jira
- Currently the underlying HTTP client uses synchronous approach (due to GH REST API rate limiting considerations)
- Make adapter/manifest layer more abstract, e.g. maybe there are common operations, those could be added to the corresponding interfaces
- Manifest layer caching of remote state could be improved
- Expand the operation list
