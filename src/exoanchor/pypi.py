import requests
from pathlib import Path
from packaging.requirements import Requirement
from packaging.version import Version, InvalidVersion

class RequirementsParser:
    def parse_file(self, file_path: Path) -> list[Requirement]:
        if not file_path.exists():
            raise FileNotFoundError(f"Requirements file not found: {file_path}")
        with open(file_path, 'r') as f:
            lines = f.readlines()
        requirements = []
        for line in lines:
            cleaned = line.strip()
            if cleaned and not cleaned.startswith('#'):
                try:
                    requirements.append(Requirement(cleaned))
                except Exception:
                    continue
        return requirements

class PyPIClient:
    def get_latest_stable_version(self, package_name: str) -> str | None:
        try:
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            stable_versions = []
            for version_str in data["releases"].keys():
                try:
                    v = Version(version_str)
                    if not v.is_prerelease:
                        stable_versions.append(v)
                except InvalidVersion:
                    continue
            if stable_versions:
                return str(max(stable_versions))
            return None
        except requests.exceptions.RequestException:
            return None
