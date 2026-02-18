import logging
from typing import Annotated

import typer

from src.configs import project_meta

logger = logging.getLogger(project_meta.name)
app = typer.Typer(pretty_exceptions_show_locals=False)


@app.command()
def hello(name: Annotated[str, typer.Option()]) -> None:
    typer.echo(f"Hello {name}!")
    return
