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

import logging

from typica.utils.log import CustomLogLevel, setup_logger

from .env import ApplicationConfig, ProjectConfig

config = ApplicationConfig()
project_meta = ProjectConfig()


setup_logger(
    **{
        "name": project_meta.name,
        "base_level": CustomLogLevel.DEBUG,
        "console": True,
        "console_level": CustomLogLevel.INFO,
        "log_dir": "./logs",
        "file_handlers_config": [
            {
                "filename": "prod_debug.log",
                "level": CustomLogLevel.DEBUG,
                "max_bytes": 5_000_000,
                "backup_count": 5,
            }
        ],
    }
)

__all__ = [logging, CustomLogLevel, config, ProjectConfig]
