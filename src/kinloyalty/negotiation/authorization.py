"""Bind approved live smoke/pilot scopes to fixed budgets and prior versions."""

from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class SmokeAuthorization:
    """Record the approved Phase 4 limits without changing the scientific configuration."""

    expected_versions: dict[str, str]
    natural_attempt_cap: int = 384
    probe_attempt_cap: int = 32
    approved_by: str = 'researcher'
    approved_on: str = '2026-11-26'
    phase: str = 'smoke'

    def contract(self, manifest_sha256: str) -> dict:
        """Return the immutable collection authorization persisted across resumptions."""
        if self.phase != 'smoke' or self.natural_attempt_cap != 384 or self.probe_attempt_cap != 32:
            raise ValueError('The approved smoke budgets are 384 natural and 32 probe attempts.')
        return {'manifest_sha256': manifest_sha256, 'execution_mode': 'live', **asdict(self)}


@dataclass(frozen=True)
class PilotAuthorization:
    """Record the explicitly approved 80-episode, 7,680-attempt pilot ceiling."""

    expected_versions: dict[str, str]
    natural_attempt_cap: int = 7680
    probe_attempt_cap: int = 0
    approved_by: str = 'researcher'
    approved_on: str = '2026-11-26'
    phase: str = 'pilot'

    def contract(self, manifest_sha256: str) -> dict:
        """Persist the phase and cumulative cap; no probes or main collection."""
        if self.phase != 'pilot' or self.natural_attempt_cap != 7680 or self.probe_attempt_cap != 0:
            raise ValueError('The approved pilot budget is 7680 natural and zero probe attempts.')
        return {'manifest_sha256': manifest_sha256, 'execution_mode': 'live', **asdict(self)}


class ModelDriftError(RuntimeError):
    """Stop live dispatch after the changed returned version has been logged."""


def study1_versions(preregistration: str | Path) -> dict[str, str]:
    """Read only the locked registration's requested/returned version table."""
    text = Path(preregistration).read_text(encoding='utf-8')
    section = text.split('## 2. Models, endpoints, and frozen API settings', 1)[1].split('## 3.', 1)[0]
    versions = {}
    for line in section.splitlines():
        columns = [column.strip() for column in line.split('|')[1:-1]]
        if len(columns) == 4 and columns[2].startswith('`') and columns[3].startswith('`'):
            versions[columns[2].strip('`')] = columns[3].strip('`')
    if len(versions) != 4:
        raise ValueError('The Study 1 registration must supply exactly four prior returned versions.')
    return versions
