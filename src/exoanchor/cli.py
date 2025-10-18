import click
from pathlib import Path
from .engine import run_analysis
from .syntax_checker import SyntaxChecker
from .models import RunResult

# --- Content for the demo files ---
DEMO_PY_CONTENT = """
\"\"\"
This is a demonstration file for the exoanchor tool.

- It is syntactically correct, so `exoanchor syntax demo.py` will pass.
- It uses a feature from an old version of NumPy that is now removed.
- `exoanchor run` will upgrade NumPy and correctly report a failure.
\"\"\"
import numpy as np

def check_old_numpy_feature():
    \"\"\"
    This function uses `np.bool`, which was deprecated and removed in NumPy 1.24.
    \"\"\"
    print(f"--> Checking with NumPy version: {np.__version__}")
    
    result = np.bool(True)
    
    assert result is True
    print("--> Old NumPy feature check passed.")

if __name__ == "__main__":
    check_old_numpy_feature()
"""
DEMO_REQS_CONTENT = "numpy==1.20.0"

@click.group()
def cli():
    """Exoanchor: A tool to anchor your project against dependency storms and syntax errors."""
    pass

@cli.command()
def demo():
    """Creates demo files to showcase exoanchor's features."""
    click.secho("--> Creating demo files...", fg="cyan")
    
    demo_py_path = Path("demo.py")
    demo_reqs_path = Path("demo_requirements.txt")

    # PREMORTEM MITIGATION #1: Prevent overwriting existing files.
    if demo_py_path.exists() or demo_reqs_path.exists():
        click.secho(f"Error: `{demo_py_path}` or `{demo_reqs_path}` already exists in this directory.", fg="red")
        click.echo("Please remove them or run this command in an empty directory.")
        return

    demo_py_path.write_text(DEMO_PY_CONTENT.strip())
    demo_reqs_path.write_text(DEMO_REQS_CONTENT.strip())
    
    click.secho(f"✅ Created `{demo_py_path}` and `{demo_reqs_path}`.", fg="green")
    click.echo("\nNow you can test exoanchor's features!")
    click.echo("\n1. Test the syntax checker (this will pass):")
    click.secho("   exoanchor syntax demo.py", bold=True)
    click.echo("\n2. Test the resilience checker (this will fail as intended):")
    click.secho(f'   exoanchor run --reqs {demo_reqs_path} --command "python3 demo.py"', bold=True)

@cli.command()
@click.option('--reqs', default='requirements.txt', help='Path to your requirements file.')
@click.option('--command', required=True, help='The test command to run (e.g., "pytest").')
@click.option('--json', 'json_output', is_flag=True, help='Output the result as a JSON object.')
def run(reqs, command, json_output):
    """Checks if your project survives a dependency upgrade."""
    try:
        # The engine is now silent and returns a structured result object.
        result = run_analysis(Path(reqs), command)

        if json_output:
            # If --json is passed, print the JSON and exit immediately.
            click.echo(result.to_json())
            return

        # PREMORTEM MITIGATION #3: Clean, human-readable output.
        # The CLI is now solely responsible for presentation.
        click.secho("🛡️  exoanchor: Dependency resilience check complete.", fg="cyan", bold=True)
        click.echo("\n" + "="*50)
        
        if result.status == "SUCCESS":
            click.secho("✅ SUCCESS: Your project survived the 'LATEST STABLE' scenario!", fg="green", bold=True)
        else:
            click.secho("💥 FAILED: Your project broke in the 'LATEST STABLE' scenario.", fg="red", bold=True)
        
        if result.log_output:
            click.echo("\n--- LOGS ---")
            click.echo(result.log_output)
        click.echo("="*50)

    except (FileNotFoundError, Exception) as e:
        # PREMORTEM MITIGATION #2: Ensure errors are also formatted as JSON if requested.
        if json_output:
            error_result = RunResult(status="ERROR", log_output=str(e), inputs={"command": command, "reqs": reqs})
            click.echo(error_result.to_json())
        else:
            click.secho(f"Error: {e}", fg="red")

@cli.command()
@click.argument('filepath', type=click.Path(exists=True, dir_okay=False))
def syntax(filepath):
    """Checks a single Python file for common syntax errors."""
    click.secho(f"✍️  exoanchor: Running syntax check on '{filepath}'...", fg="cyan", bold=True)
    checker = SyntaxChecker(filepath)
    errors = checker.check()

    if not errors:
        click.secho("✅ No syntax errors found!", fg="green")
        return

    click.secho(f"💥 Found {len(errors)} error(s):", fg="red", bold=True)
    for error in errors:
        click.echo(f"  {click.style(filepath, fg='yellow')}:{click.style(str(error.line), fg='cyan')}:{click.style(str(error.col), fg='cyan')} [{click.style(error.code, fg='red', bold=True)}] {error.message}")

# The entry point for pyproject.toml, pointing to the main command group.
main = cli