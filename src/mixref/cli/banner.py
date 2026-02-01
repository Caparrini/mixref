"""Banner and logo for mixref interactive mode."""

from rich.console import Console


def show_banner(console: Console | None = None) -> None:
    """
    Display the mixref banner with colored ASCII art logo.

    Args:
        console: Rich Console instance. If None, creates a new one.

    Example:
        >>> from mixref.cli.banner import show_banner
        >>> show_banner()
    """
    if console is None:
        console = Console()

    console.print()
    # Audio waveform visualization
    console.print(
        "  [bright_cyan]▁▂▃▅▆▇█[/][cyan]█▇▆▅▃▂▁[/]  "
        "[bright_magenta]▁▂▃▅▆▇█[/][magenta]█▇▆▅▃▂▁[/]  "
        "[bright_yellow]▁▂▃▅▆▇█[/][yellow]█▇▆▅▃▂▁[/]"
    )
    console.print()

    # mixref ASCII art with color gradient
    console.print(
        "   [bold bright_cyan]███╗   ███╗[/] [bold cyan]██╗[/] "
        "[bold bright_magenta]██╗  ██╗[/] [bold magenta]██████╗[/]  "
        "[bold bright_yellow]███████╗[/] [bold yellow]███████╗[/]"
    )
    console.print(
        "   [bold bright_cyan]████╗ ████║[/] [bold cyan]██║[/] "
        "[bold bright_magenta]╚██╗██╔╝[/] [bold magenta]██╔══██╗[/] "
        "[bold bright_yellow]██╔════╝[/] [bold yellow]██╔════╝[/]"
    )
    console.print(
        "   [bold bright_cyan]██╔████╔██║[/] [bold cyan]██║[/] "
        "[bold bright_magenta] ╚███╔╝[/]  [bold magenta]██████╔╝[/] "
        "[bold bright_yellow]█████╗[/]   [bold yellow]█████╗[/]  "
    )
    console.print(
        "   [bold cyan]██║╚██╔╝██║[/] [bold cyan]██║[/] "
        "[bold magenta] ██╔██╗[/]  [bold magenta]██╔══██╗[/] "
        "[bold yellow]██╔══╝[/]   [bold yellow]██╔══╝[/]  "
    )
    console.print(
        "   [bold cyan]██║ ╚═╝ ██║[/] [bold cyan]██║[/] "
        "[bold magenta]██╔╝ ██╗[/] [bold magenta]██║  ██║[/] "
        "[bold yellow]███████╗[/] [bold yellow]██║[/]     "
    )
    console.print(
        "   [bold dim cyan]╚═╝     ╚═╝[/] [bold dim cyan]╚═╝[/] "
        "[bold dim magenta]╚═╝  ╚═╝[/] [bold dim magenta]╚═╝  ╚═╝[/] "
        "[bold dim yellow]╚══════╝[/] [bold dim yellow]╚═╝[/]     "
    )

    console.print()
    # Audio waveform visualization (bottom)
    console.print(
        "  [bright_yellow]▁▂▃▅▆▇█[/][yellow]█▇▆▅▃▂▁[/]  "
        "[bright_cyan]▁▂▃▅▆▇█[/][cyan]█▇▆▅▃▂▁[/]  "
        "[bright_magenta]▁▂▃▅▆▇█[/][magenta]█▇▆▅▃▂▁[/]"
    )
    console.print()

    console.print("           [dim]CLI Audio Analyzer for Music Producers[/]")
    console.print()
