from pathlib import Path
from .pypi import RequirementsParser, PyPIClient
from .sandbox import SandboxRunner

def run_analysis(reqs_path: Path, command: str) -> tuple[bool, str]:
    """
    The core logic engine for exoanchor.
    Returns a tuple of (success_boolean, combined_output_log).
    """
    print(f"--> Parsing requirements from '{reqs_path.name}'...")
    parser = RequirementsParser()
    pypi = PyPIClient()
    
    base_requirements = parser.parse_file(reqs_path)
    if not base_requirements:
        return True, "No requirements found to test. Exiting."

    print(f"--> Finding latest stable versions for {len(base_requirements)} packages on PyPI...")
    future_packages = []
    for req in base_requirements:
        latest_version = pypi.get_latest_stable_version(req.name)
        if latest_version:
            pin = f"{req.name}=={latest_version}"
            print(f"    - {req.name} -> {latest_version}")
            future_packages.append(pin)
        else:
            print(f"    - Could not find version for {req.name}, skipping.")

    if not future_packages:
        return False, "Could not determine any future package versions to test. Exiting."

    print(f"--> Creating secure sandbox and running command: '{command}'")
    runner = SandboxRunner(test_command=command, packages_to_install=future_packages)
    success, output = runner.run()
    return success, output