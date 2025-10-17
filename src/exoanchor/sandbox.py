import sys
import subprocess
import shutil
from pathlib import Path

class SandboxRunner:
    def __init__(self, test_command: str, packages_to_install: list[str]):
        self.test_command = test_command
        self.packages_to_install = packages_to_install
        self.sandbox_dir = Path("./exoanchor_sandbox")

    def run(self) -> tuple[bool, str]:
        try:
            self._create_sandbox()
            self._install_packages()
            success, output = self._run_command()
            return success, output
        except subprocess.CalledProcessError as e:
            # NEW: Catch installation/setup errors and report them gracefully
            error_output = f"A setup command failed:\n--- STDOUT ---\n{e.stdout}\n--- STDERR ---\n{e.stderr}"
            return False, error_output
        finally:
            self._destroy_sandbox()

    def _create_sandbox(self):
        self.sandbox_dir.mkdir(exist_ok=True)
        self.venv_dir = self.sandbox_dir / ".venv"
        subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True, capture_output=True, text=True)
        
        # NEW: Windows compatibility check
        if sys.platform == "win32":
            self.python_executable = self.venv_dir / "Scripts" / "python.exe"
        else:
            self.python_executable = self.venv_dir / "bin" / "python"

    def _install_packages(self):
        print("--> Installing dependencies in sandbox... (This may take a moment)")
        for package in self.packages_to_install:
            subprocess.run(
                [str(self.python_executable), "-m", "pip", "install", "-q", package],
                check=True, capture_output=True, text=True
            )
        print("--> Installation complete.")

    def _run_command(self) -> tuple[bool, str]:
        result = subprocess.run(
            self.test_command, shell=True, capture_output=True, text=True, cwd="."
        )
        output = result.stdout + "\n" + result.stderr
        return result.returncode == 0, output.strip()

    def _destroy_sandbox(self):
        if self.sandbox_dir.exists():
            shutil.rmtree(self.sandbox_dir)
