from typer.testing import CliRunner

from src.main import app

runner = CliRunner()


def test_greet():
    result = runner.invoke(app, ["base", "hello", "--name", "okta"])
    assert result.exit_code == 0
    assert "Hello okta!" in result.output
