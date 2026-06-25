import logging
import sys

import typer

from pa_cli.cli.init_cmd import app as init_app
from pa_cli.cli.files_cmd import app as files_app
from pa_cli.cli.consoles_cmd import app as consoles_app
from pa_cli.cli.webapps_cmd import app as webapps_app
from pa_cli.cli.deploy_cmd import app as deploy_app
from pa_cli.cli.account_cmd import app as account_app
from pa_cli.cli.register_cmd import app as register_app
from pa_cli.cli.status_cmd import app as status_app
from pa_cli.cli.tasks_cmd import app as tasks_app
from pa_cli.cli.always_on_cmd import app as always_on_app
from pa_cli.cli.databases_cmd import app as databases_app

try:
    from importlib.metadata import version
    __version__ = version("pa-cli")
except Exception:
    __version__ = "0.0.0"


def version_callback(value: bool):
    if value:
        typer.echo(f"pa-cli {__version__}")
        raise typer.Exit()


def verbose_callback(value: bool):
    if value:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            stream=sys.stderr,
        )
    return value


app = typer.Typer(
    help="CLI tool for automating PythonAnywhere deployments.",
    no_args_is_help=True,
)


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit", callback=version_callback, is_eager=True),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging", callback=verbose_callback, is_eager=True),
):
    pass

# Direct commands (single command)
app.add_typer(init_app, name="init", help="Configure PythonAnywhere account")
app.add_typer(deploy_app, name="deploy", help="Deploy a local project to PythonAnywhere")
app.add_typer(register_app, name="register", help="Register a new PythonAnywhere account")

# Command groups (multiple subcommands)
app.add_typer(files_app, name="files", help="Manage files on PythonAnywhere")
app.add_typer(consoles_app, name="console", help="Manage consoles on PythonAnywhere")
app.add_typer(webapps_app, name="webapp", help="Manage web apps on PythonAnywhere")
app.add_typer(account_app, name="account", help="Account management")
app.add_typer(status_app, name="status", help="Query system status and resource usage")
app.add_typer(tasks_app, name="tasks", help="Manage scheduled tasks on PythonAnywhere")
app.add_typer(always_on_app, name="always-on", help="Manage always-on tasks on PythonAnywhere")
app.add_typer(databases_app, name="databases", help="Manage databases on PythonAnywhere")


if __name__ == "__main__":
    app()
