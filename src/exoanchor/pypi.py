import requests
from pathlib import Path
from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion

class RequirementsParser:
    """Parses a requirements.txt file into a list of Requirement objects."""
    def parse_file(self, file_path: Path) -> list[Requirement]:
        if not file_path.exists():
            raise FileNotFoundError(f"Requirements file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            lines = f.readlines()

        requirements = []
        for line in lines:
            cleaned = line.strip()
            # Skip empty lines and comments
            if cleaned and not cleaned.startswith('#'):
                try:
                    requirements.append(Requirement(cleaned))
                except Exception:
                    # For our lean version, we silently ignore invalid lines
                    continue
        return requirements

class PyPIClient:
    """Client for interacting with the PyPI JSON API to find package versions."""
    def get_latest_stable_version(self, package_name: str) -> str | None:
        """
        Fetches the latest, non-prerelease version string for a package.
        Returns None if the package is not found or an error occurs.
        """
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raises an exception for 4xx/5xx errors
            data = response.json()
            
            stable_versions = []
            for version_str in data["releases"].keys():
                try:
                    v = Version(version_str)
                    if not v.is_prerelease:
                        stable_versions.append(v)
                except InvalidVersion:
                    # Ignore malformed version strings
                    continue
            
            if stable_versions:
                return str(max(stable_versions))
            return None # No stable versions found
        except requests.exceptions.RequestException:
            # Covers connection errors, timeouts, 404s, etc.
            return None