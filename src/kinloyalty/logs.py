"""Persist append-only JSONL attempts with an atomic in-flight journal and run lock."""

import fcntl
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def json_line(value: Any) -> str:
    """Serialize deterministic JSON without reordering schema properties or allowing NaN."""
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n"


def content_hash(value: Any) -> str:
    """Hash exact serialized content, including scientifically relevant property order."""
    return hashlib.sha256(json_line(value).encode("utf-8")).hexdigest()


def file_hash(path: str | Path) -> str:
    """Return a SHA-256 digest of a saved artifact's exact bytes."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read complete JSON objects, failing on corrupt or interrupted writes."""
    path = Path(path)
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.endswith("\n"):
                raise ValueError(f"Incomplete JSONL record at {path}:{number}; preserve the file for recovery.")
            try:
                record = json.loads(line)
            except (ValueError, RecursionError) as error:
                raise ValueError(f"Invalid JSONL record at {path}:{number}.") from error
            if not isinstance(record, dict):
                raise ValueError(f"Expected a JSON object at {path}:{number}.")
            records.append(record)
    return records


def assert_no_credentials(value: Any) -> None:
    """Reject credential/header fields in artifacts; never inspect environment secrets."""
    forbidden = {"api_key", "apikey", "authorization", "headers", "request_headers", "access_token", "refresh_token"}
    if isinstance(value, dict):
        if any(str(key).lower().replace("-", "_") in forbidden for key in value):
            raise ValueError("Credentials or headers are forbidden in research artifacts.")
        for child in value.values():
            assert_no_credentials(child)
    elif isinstance(value, list):
        for child in value:
            assert_no_credentials(child)


def _sync_directory(directory: Path) -> None:
    descriptor = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


class AttemptLog:
    """Serialize one local runner and preserve unfinished reservations across restarts."""

    def __init__(self, path: str | Path) -> None:
        """Set append-only log and sidecar paths without writing them yet."""
        self.path = Path(path)
        self.pending_path = self.path.with_name(self.path.name + ".pending.json")
        self.lock_path = self.path.with_name(self.path.name + ".lock")
        self.records: list[dict[str, Any]] = []
        self.pending: dict[str, dict[str, Any]] = {}
        self._lock = None

    def __enter__(self) -> "AttemptLog":
        """Lock the log before reading it; concurrent writers fail without making calls."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = self.lock_path.open("a+b")
        try:
            fcntl.flock(self._lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.records = read_jsonl(self.path)
            if self.pending_path.exists():
                self.pending = json.loads(self.pending_path.read_text(encoding="utf-8"))
            return self
        except BaseException:
            self._lock.close()
            self._lock = None
            raise

    def __exit__(self, *args: Any) -> None:
        """Release the process lock while leaving the audit artifacts intact."""
        if self._lock is not None:
            self._lock.close()
            self._lock = None

    def _save_pending(self) -> None:
        if not self.pending:
            self.pending_path.unlink(missing_ok=True)
            _sync_directory(self.path.parent)
            return
        descriptor, temporary = tempfile.mkstemp(prefix=self.pending_path.name + ".", dir=self.path.parent)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write(json_line(self.pending))
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.pending_path)
            _sync_directory(self.path.parent)
        finally:
            Path(temporary).unlink(missing_ok=True)

    def reserve(self, record: dict[str, Any]) -> None:
        """Durably save attempt identity and frozen request before a client is called."""
        assert_no_credentials(record)
        self.pending[record["record_id"]] = record
        self._save_pending()

    def recover_pending(self, completed_at_utc: str) -> int:
        """Record interrupted reservations once; never infer an unseen answer or exclusion."""
        completed = {record["record_id"] for record in self.records}
        recovered = 0
        for record_id, record in sorted(list(self.pending.items()), key=lambda item: item[1]["dispatch_sequence"]):
            if record_id in completed:
                self.pending.pop(record_id)
                continue
            record["completed_at_utc"] = completed_at_utc
            record["latency_seconds"] = None
            record["api_error"] = {"kind": "interrupted", "retryable": True, "status_code": None}
            self.append(record)
            recovered += 1
        self._save_pending()
        return recovered

    def append(self, record: dict[str, Any]) -> None:
        """Append and fsync exactly one completed/interrupted attempt, then clear its reservation."""
        assert_no_credentials(record)
        encoded = json_line(record).encode("utf-8")
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            remaining = memoryview(encoded)
            while remaining:
                count = os.write(descriptor, remaining)
                if not count:
                    raise OSError("JSONL append did not make progress.")
                remaining = remaining[count:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self.records.append(record)
        self.pending.pop(record["record_id"], None)
        self._save_pending()
