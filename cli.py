import inspect
from functools import wraps
from pathlib import Path
from typing import Any

from rich import print as rich_print
from typer import Typer

from main import GitHubAdapter
from manifest import GitHubManifest

cli = Typer()
gh = Typer()

gh_adapter = GitHubAdapter()


def report_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        rich_print(result)

    return wrapper


def register_subcommands(cmd: Typer, source_obj: Any):
    for name, func in inspect.getmembers(source_obj, predicate=inspect.ismethod):
        if not name.startswith("_"):
            cmd.command(name.replace("_", "-"))(report_result(func))


register_subcommands(gh, gh_adapter)


@gh.command("apply-manifest")
def apply_manifest(path: Path):
    manifest = GitHubManifest(path)
    rich_print(manifest.manifest().model_dump(mode="json"))


cli.add_typer(gh, name="gh")

if __name__ == "__main__":
    cli()
