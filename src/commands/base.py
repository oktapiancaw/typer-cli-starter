# Copyright (C) 2026 Nama Anda
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
