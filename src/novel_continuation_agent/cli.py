from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from novel_continuation_agent import __version__
from novel_continuation_agent.agent import build_status

app = typer.Typer(help="Novel continuation agent skeleton.")
console = Console()


@app.callback()
def main() -> None:
    load_dotenv()


@app.command()
def version() -> None:
    """Show package version."""
    console.print(__version__)


@app.command()
def status(root: Path = typer.Option(Path.cwd(), help="Project root directory.")) -> None:
    """Show current project paths and planned pipeline stages."""
    current_status = build_status(root)

    console.print(f"[bold]{current_status.project_name}[/bold] v{current_status.version}")

    path_table = Table(title="Project Paths")
    path_table.add_column("Name")
    path_table.add_column("Path")
    for name, value in current_status.paths.model_dump().items():
        path_table.add_row(name, str(value))
    console.print(path_table)

    stage_table = Table(title="Pipeline Stages")
    stage_table.add_column("Order")
    stage_table.add_column("Stage")
    for index, stage in enumerate(current_status.stages, start=1):
        stage_table.add_row(str(index), stage.value)
    console.print(stage_table)
