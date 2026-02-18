
---
# Typer CLI Starter
**This is starter template for creating a CLI project using Typer framework**



*\* Disclaimer:*
> *The description and all doc strings were created with the help of AI, so please forgive any writing errors. The coding was done by myself.*
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

| Group | Command |
| --- | --- |
| **All Groups** | `uv sync --all-groups` |
| **Kafka** | `uv sync --group kafka` |
| **PostgreSQL** | `uv sync --group postgresql` |
| **Elasticsearch** | `uv sync --group elastic` |
| **MongoDB** | `uv sync --group mongo` |
| **RabbitMQ** | `uv sync --group rmq` |

---

## Usage with uv run

One of the best features of `uv` is running your script without manually managing the virtual environment. It will respect your groups if you've synced them:

```bash
# Run the CLI directly
uv run python src/main.py --help
```
If you notice, in pyprojectoml in the project.scripts section, there is a command, and it can be run like this

```bash
# Run the CLI directly
uv run cli-exec
```


## Contributors

[//]: contributor-faces

<a href="https://github.com/oktapiancaw"><img src="https://avatars.githubusercontent.com/u/48079010?v=4" title="Oktapian Candra" width="80" height="80" style="border-radius: 50%"></a>

[//]: contributor-faces
