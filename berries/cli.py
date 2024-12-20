"""Console script for arjanrulz."""

import asyncio
import itertools

import typer
import berries
from rich.console import Console

app = typer.Typer()
console = Console()


async def _filter_berries(generator, name: str | None = None):
    async for berry in generator:
        if name is None or berry.name.startswith(name):
            yield berry


async def _fetch_berries(name: str | None = None) -> None:
    """Fetch Berries from the API and print them to the console."""
    berry = await berries.get_app()

    console.print(f"Retrieving Berries which its name starts with: {name}")
    filtered_generator = _filter_berries(berry.service.get_all_generator(), name)
    async for berry in filtered_generator: 
        console.print(f"Berry ID: {berry.id}")
        console.print(f"Berry Name: {berry.name}")
        console.print(f"Berry Firmness: {berry.firmness.name}")
        console.print("-" * 50)


@app.command()
def list_berries(name: str = typer.Option(None, help="Fetch berries that starts with this name.")):
    """List all Berries."""
    console.print("Welcome to the Berries App!")
    console.print("Retrieving Berries information...")
    asyncio.run(_fetch_berries(name))


if __name__ == "__main__":
    app()
