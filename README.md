# Typer CLI Starter
This is Starter template for creating a CLI project using Typer framework
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


> **Disclaimer:**
>
> *The description and all doc strings were created with the help of AI, so please forgive any writing errors🙏. But the script was done by myself😠.*
>
> \- Okta

## Prerequisites

Before starting the application, ensure you have uv installed. You can install the dependencies and set up the virtual environment in one of the following ways:

### Standard Installation

To install the core CLI dependencies (Typer, etc.):

```bash
uv sync & uv lock
```

### Installing Optional Data Drivers

Since this boilerplate supports various data sources, you can install specific dependency groups depending on your engine's requirements:

| Group | Command | Description |
| --- | --- | --- |
| **All Groups** | `uv sync --all-groups` | Install All drivers |
| **CKafka** | `uv sync --group kafka` | Install Conflunet Kafka driver |
| **PostgreSQL** | `uv sync --group postgresql` | Install Psycopg driver |
| **PG Alchemy** | `uv sync --group pg-alchemy` | Install SQLAlchemy, Pandas, Psycopg drivers | 
| **Elasticsearch** | `uv sync --group elastic` | Install Elasticsearch 7 & 8 Drivers |
| **MongoDB** | `uv sync --group mongo` | Install PyMongo driver |
| **RabbitMQ** | `uv sync --group rmq` | Install Pika driver |

---

then you can use the driver located in the `src/connection/**/*.py` path

## Usage with uv run

One of the best features of `uv` is running your script without manually managing the virtual environment. It will respect your groups if you've synced them:

```bash
# Run the CLI directly
uv run python src/main.py --help
```
If you notice, in `pyproject.toml` in the *project.scripts* section, there is a command, and it can be run like this

```bash
# Run the CLI directly
uv run cli-exec
```

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.

```text
Copyright (C) 2026 Oktapiancaw
```

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [LICENSE](LICENSE) file for more details.


## Contributors

[//]: contributor-faces

<a href="https://github.com/oktapiancaw"><img src="https://avatars.githubusercontent.com/u/48079010?v=4" title="Oktapian Candra" width="80" height="80" style="border-radius: 50%"></a>

[//]: contributor-faces
