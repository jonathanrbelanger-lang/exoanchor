import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

@dataclass
class RunResult:
    """A data structure to hold the complete result of an exoanchor run."""
    status: str
    log_output: str
    inputs: dict
    checked_packages: list[dict] = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_json(self) -> str:
        """Serializes the result object to a JSON string."""
        return json.dumps(asdict(self), indent=2)