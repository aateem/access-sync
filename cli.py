import inspect
from functools import wraps
from typing import Any

from rich import print as rich_print
from typer import Typer

from main import GitHubAdapter

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

cli.add_typer(gh, name="gh")

if __name__ == "__main__":
    cli()
