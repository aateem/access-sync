import inspect
import sys
from functools import wraps
from pathlib import Path
from typing import Any

import yaml
from loguru import logger
from rich import print as rich_print
from typer import Typer

from access_manager.adapter import GitHubAdapter
from access_manager.manifest import GitHubManifest

cli = Typer()
gh = Typer()

gh_adapter = GitHubAdapter()


def report_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        rich_print(result)

    return wrapper


# NOTE: this is a quick way to auto-register subcommands
# though now one needs to be careful not expose "private" methods
def register_subcommands(cmd: Typer, source_obj: Any):
    for name, func in inspect.getmembers(source_obj, predicate=inspect.ismethod):
        if not name.startswith("_"):
            cmd.command(name.replace("_", "-"))(report_result(func))


register_subcommands(gh, gh_adapter)


@gh.command("apply-manifest")
def apply_manifest(path: Path):
    with open(path) as f:
        data = yaml.safe_load(f.read())
    manifest = GitHubManifest(manifest_data=data, github_adapter=gh_adapter)
    manifest.apply()


cli.add_typer(gh, name="gh")


@cli.callback()
def configure(log_level: str = "INFO"):
    # remove the default logger configuration
    logger.remove()

    logger.add(sys.stderr, level=log_level)


if __name__ == "__main__":
    cli()
