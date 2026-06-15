import typer

from pa_cli.cli.init_cmd import app as init_app
from pa_cli.cli.files_cmd import app as files_app
from pa_cli.cli.consoles_cmd import app as consoles_app
from pa_cli.cli.webapps_cmd import app as webapps_app
from pa_cli.cli.deploy_cmd import app as deploy_app
from pa_cli.cli.account_cmd import app as account_app
from pa_cli.cli.register_cmd import app as register_app
from pa_cli.cli.status_cmd import app as status_app

app = typer.Typer(
    help="CLI tool for automating PythonAnywhere deployments.",
    no_args_is_help=True,
)

app.add_typer(init_app, name="init", help="Configure PythonAnywhere account")
app.add_typer(files_app, name="files", help="Manage files on PythonAnywhere")
app.add_typer(consoles_app, name="console", help="Manage consoles on PythonAnywhere")
app.add_typer(webapps_app, name="webapp", help="Manage web apps on PythonAnywhere")
app.add_typer(deploy_app, name="deploy", help="Deploy a local project to PythonAnywhere")
app.add_typer(account_app, name="account", help="Account management")
app.add_typer(register_app, name="register", help="Register a new PythonAnywhere account")
app.add_typer(status_app, name="status", help="Query system status and resource usage")


if __name__ == "__main__":
    app()
