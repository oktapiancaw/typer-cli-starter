# Copyright (C) 2026 Oktapiancaw
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import typer

from src.commands import base
from src.configs import CustomLogLevel, logging, project_meta

app = typer.Typer(pretty_exceptions_show_locals=False)

LOGGER = logging.getLogger(project_meta.name)

app.add_typer(base.app, name="base")


@app.callback()
def main(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
):
    if verbose:
        logging.getLogger().setLevel(CustomLogLevel.INFO)
        LOGGER.debug("Verbose mode enabled")
    else:
        logging.getLogger().setLevel(CustomLogLevel.NOTSET)


if __name__ == "__main__":
    app()
