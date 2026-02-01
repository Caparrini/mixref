"""Main CLI entry point for mixref."""

import typer
from rich.console import Console

from mixref import __version__
from mixref.cli.analyze import analyze_command
from mixref.cli.banner import show_banner
from mixref.cli.compare import compare_command

app = typer.Typer(
    name="mixref",
    help="CLI Audio Analyzer for Music Producers - DnB, Techno, House",
    add_completion=False,
    invoke_without_command=True,
    no_args_is_help=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        show_banner(console)
        console.print(f"[bold]version[/] {__version__}\n")
        raise typer.Exit()


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    mixref - Audio analysis for producers who know what they want.

    Sharp, opinionated insights for electronic music production.
    """
    # Show banner when no command is invoked
    if ctx.invoked_subcommand is None:
        show_banner(console)
        # Show help after banner
        console.print(ctx.get_help())
        raise typer.Exit()


# Register commands
app.command(name="analyze")(analyze_command)
app.command(name="compare")(compare_command)


if __name__ == "__main__":
    app()
