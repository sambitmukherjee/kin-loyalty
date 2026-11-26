"""Preserve arbitrary model reply content while checking transport metadata for secrets."""

import os
from copy import deepcopy
from typing import Any

from kinloyalty.logs import AttemptLog, assert_no_credentials, json_line


def _check_metadata(record: dict[str, Any]) -> None:
    # A supplied non-offer price may be any JSON value, including an object whose
    # keys look like headers. That is reply content, not HTTP headers. Adapters
    # capture bodies only; actual transport metadata and requests stay checked.
    assert_no_credentials({key: value for key, value in record.items() if key not in {'response', 'validation'}})


class Study2Log(AttemptLog):
    """Reuse locking/pending journals with a reply-aware artifact field policy."""

    def reserve(self, record: dict[str, Any]) -> None:
        """Fsync a checked reservation before a client can be invoked."""
        _check_metadata(record)
        self.pending[record['record_id']] = deepcopy(record)
        self._save_pending()

    def append(self, record: dict[str, Any]) -> None:
        """Append the exact reply without interpreting arbitrary content as transport data."""
        _check_metadata(record)
        encoded = json_line(record).encode('utf-8')
        descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            remaining = memoryview(encoded)
            while remaining:
                count = os.write(descriptor, remaining)
                if not count:
                    raise OSError('JSONL append did not make progress.')
                remaining = remaining[count:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        self.records.append(deepcopy(record))
        self.pending.pop(record['record_id'], None)
        self._save_pending()
