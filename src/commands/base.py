import logging
from typing import Annotated

import typer

logger = logging.getLogger(__name__)
app = typer.Typer(pretty_exceptions_show_locals=False)


@app.command()
def hello(name: Annotated[str, typer.Option()]) -> None:
    typer.echo(f"Hello {name}!")
    return
