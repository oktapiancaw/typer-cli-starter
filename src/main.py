import typer

from src.configs.log import LOGGER, logging
from src.commands import base


app = typer.Typer(pretty_exceptions_show_locals=False)


app.add_typer(base.app, name="base")


@app.callback()
def main(verbose: bool = typer.Option(False, "--verbose", "-v")):
    level = logging.INFO
    if verbose:
        level = 1

    LOGGER.setLevel(level)


if __name__ == "__main__":
    app()
