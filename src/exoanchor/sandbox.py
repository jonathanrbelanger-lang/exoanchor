import sys
import subprocess
import shutil
from pathlib import Path
import os

class SandboxRunner:
    """Creates an isolated Python environment to safely execute a test command."""
    def __init__(self, test_command: str, packages_to_install: list[str]):
        self.test_command = test_command
        self.packages_to_install = packages_to_install
        self.sandbox_dir = Path("./exoanchor_sandbox")

    def run(self) -> tuple[bool, str]:
        """
        Orchestrates the entire sandbox lifecycle: create, install, run, destroy.
        Returns a tuple of (success_boolean, combined_output_log).
        """
        try:
            self._create_sandbox()
            self._install_packages()
            success, output = self._run_command()
            return success, output
        except subprocess.CalledProcessError as e:
            # Catch installation/setup errors and report them gracefully
            error_output = f"A setup command failed:\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}"
            return False, error_output
        finally:
            # This `finally` block ensures cleanup happens even if an error occurs
            self._destroy_sandbox()

    def _create_sandbox(self):
        """Creates the sandbox directory and a virtual environment inside it."""
        self.sandbox_dir.mkdir(exist_ok=True)
        self.venv_dir = self.sandbox_dir / ".venv"
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True, capture_output=True, text=True)
        
        # Windows compatibility check
        if sys.platform == "win32":
            self.python_executable = self.venv_dir / "Scripts" / "python.exe"
        else:
            self.python_executable = self.venv_dir / "bin" / "python"

    def _install_packages(self):
        """Installs all specified packages using pip inside the venv."""
        print("--> Installing dependencies in sandbox... (This may take a moment)")
        for package in self.packages_to_install:
            subprocess.run(
                [str(self.python_executable), "-m", "pip", "install", "-q", package],
                check=True, capture_output=True, text=True
            )
        print("--> Installation complete.")

    def _run_command(self) -> tuple[bool, str]:
        """
        Runs the user's test command inside the activated venv by
        prepending the sandbox's bin directory to the PATH.
        """
        # Create a copy of the current environment variables
        env = os.environ.copy()
        
        # Prepend our sandbox's script/binary directory to the PATH.
        # This ensures that when `python3` is called, it finds our
        # sandboxed version first. This is the magic step.
        sandbox_bin_dir = str(self.python_executable.parent)
        env['PATH'] = sandbox_bin_dir + os.pathsep + env['PATH']

        result = subprocess.run(
            self.test_command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=".",
            env=env  # Pass the modified environment to the subprocess
        )
        output = result.stdout + "\n" + result.stderr
        return result.returncode == 0, output.strip()

    def _destroy_sandbox(self):
        """Completely removes the sandbox directory and all its contents."""
        if self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir)