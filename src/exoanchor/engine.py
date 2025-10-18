from pathlib import Path
from .pypi import RequirementsParser, PyPIClient
from .sandbox import SandboxRunner
from .models import RunResult

def find_requirements_file(start_path: Path) -> Path | None:
    """
    Searches for 'requirements.txt' in the current directory or parents.
    """
    if start_path.is_file() and start_path.exists():
        return start_path
    
    current_dir = Path.cwd()
    for directory in [current_dir] + list(current_dir.parents):
        req_file = directory / 'requirements.txt'
        if req_file.exists():
            print(f"--> Found '{req_file.relative_to(Path.cwd())}'")
            return req_file
    return None

def run_analysis(reqs_path: Path, command: str) -> RunResult:
    """The core logic engine for exoanchor."""
    print(f"--> Locating requirements file...")
    found_reqs_path = find_requirements_file(reqs_path)
    if not found_reqs_path:
        raise FileNotFoundError(f"Could not find '{reqs_path.name}' in the current directory or any parent directories.")

    parser = RequirementsParser()
    pypi = PyPIClient()
    
    base_requirements = parser.parse_file(found_reqs_path)
    if not base_requirements:
        return RunResult(status="SUCCESS", log_output="Requirements file is empty. Nothing to test.", inputs={"command": command, "reqs": str(reqs_path)})

    print(f"--> Finding latest stable versions for {len(base_requirements)} packages on PyPI...")
    future_packages = []
    checked_packages_data = []
    for req in base_requirements:
        latest_version = pypi.get_latest_stable_version(req.name)
        if latest_version:
            pin = f"{req.name}=={latest_version}"
            print(f"    - {req.name} -> {latest_version}")
            future_packages.append(pin)
            checked_packages_data.append({"name": req.name, "resolved_version": latest_version})
        else:
            print(f"    - Could not find version for {req.name}, skipping.")

    if not future_packages:
        return RunResult(status="FAILURE", log_output="Could not determine any future package versions to test.", inputs={"command": command, "reqs": str(reqs_path)})

    print(f"--> Creating secure sandbox and running command: '{command}'")
    runner = SandboxRunner(test_command=command, packages_to_install=future_packages)
    success, output = runner.run()

    return RunResult(
        status="SUCCESS" if success else "FAILURE",
        log_output=output,
        inputs={"requirements_file": str(found_reqs_path), "test_command": command},
        checked_packages=checked_packages_data
    )