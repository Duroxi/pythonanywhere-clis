import typer

from pa_cli.crawler.account_crawler import AccountCrawler

app = typer.Typer(help="Register a new PythonAnywhere account.")


@app.command()
def register():
    """Register a new PythonAnywhere account."""
    username = typer.prompt("Username (letters and numbers only)")
    email = typer.prompt("Email")
    password = typer.prompt("Password", hide_input=True)
    confirm_password = typer.prompt("Confirm password", hide_input=True)

    if password != confirm_password:
        typer.echo("Passwords do not match.", err=True)
        raise typer.Exit(code=1)

    try:
        crawler = AccountCrawler()
        crawler.register(username, email, password)
        typer.echo(f"Account '{username}' registered successfully!")
        typer.echo("Please check your email to verify your account.")
        typer.echo("Then run: pa init")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)
