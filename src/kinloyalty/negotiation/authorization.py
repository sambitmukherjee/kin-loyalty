"""Bind approved live collection scopes to immutable provenance and prior versions."""

from dataclasses import asdict, dataclass
from pathlib import Path


REGISTRATION_COMMIT = 'c277054e182eb3a81a475108fa3439e96e869bb0'
MAIN_MANIFEST_SHA256 = '293fecc0f30249e46a794d3d4e1d7d2eacb51e3ad2e13b2113da7067e0a7b814'


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


@dataclass(frozen=True)
class MainAuthorization:
    """Bind the approved main run and every resumption to both immutable revisions."""

    expected_versions: dict[str, str]
    execution_git_commit: str
    registration_git_commit: str = REGISTRATION_COMMIT
    # The researcher requested completion/resumption of all 960 episodes, without
    # an aggregate cap. Each response still has the registered four-attempt rule.
    natural_attempt_cap: None = None
    probe_attempt_cap: int = 0
    approved_by: str = 'researcher'
    approved_on: str = '2026-11-26'
    phase: str = 'main'

    def contract(self, manifest_sha256: str) -> dict:
        """Reject any other manifest, phase, registration, probes, or mutable budget."""
        if (self.phase != 'main' or manifest_sha256 != MAIN_MANIFEST_SHA256 or
                self.registration_git_commit != REGISTRATION_COMMIT or self.probe_attempt_cap != 0 or
                self.natural_attempt_cap is not None or len(self.execution_git_commit) != 40 or
                any(char not in '0123456789abcdef' for char in self.execution_git_commit)):
            raise ValueError('Main authorization must bind the registered 960-episode plan and execution revision.')
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
