"""Prevent accidental networking during offline protocol and engine tests."""

import socket

import pytest


@pytest.fixture(autouse=True)
def block_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail any attempted socket connection in the pytest process."""
    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("Network access is forbidden in offline tests.")

    monkeypatch.setattr(socket, "create_connection", fail)
    monkeypatch.setattr(socket.socket, "connect", fail)
