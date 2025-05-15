import logging

import typer

from src.commands import base
from src.configs.log import CustomLogLevel, setup_logging

app = typer.Typer(pretty_exceptions_show_locals=False)

# ? Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


app.add_typer(base.app, name="base")


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    if verbose:
        logging.getLogger().setLevel(CustomLogLevel.INFO)
        logger.debug("Verbose mode enabled")
    else:
        logging.getLogger().setLevel(CustomLogLevel.NOTSET)


if __name__ == "__main__":
    app()
