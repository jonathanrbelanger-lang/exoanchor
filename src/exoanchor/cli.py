import click
from pathlib import Path
from .engine import run_analysis # NEW: Import the engine

@click.command()
@click.option('--reqs', default='requirements.txt', help='Path to your requirements file.')
@click.option('--command', required=True, help='The test command to run (e.g., "pytest").')
def run(reqs, command):
    """Checks if your project survives a dependency upgrade."""
    click.secho("🛡️  exoanchor: Anchoring your project against future dependency storms.", fg="cyan", bold=True)
    
    try:
        success, output = run_analysis(Path(reqs), command)

        click.echo("\n" + "="*50)
        if success and "FAILED" not in output.upper(): # Check output for failure messages too
            click.secho("✅ SUCCESS: Your project survived the 'LATEST STABLE' scenario!", fg="green", bold=True)
            if output:
                click.echo("\n--- LOGS ---")
                click.echo(output)
        else:
            click.secho("💥 FAILED: Your project broke in the 'LATEST STABLE' scenario.", fg="red", bold=True)
            click.echo("\n--- LOGS ---")
            click.echo(output)
        click.echo("="*50)

    except FileNotFoundError as e:
        click.secho(f"Error: {e}", fg="red")
    except Exception as e:
        click.secho(f"An unexpected error occurred: {e}", fg="red")