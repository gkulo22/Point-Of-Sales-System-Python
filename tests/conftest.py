from sqlite3 import Connection

import pytest
from starlette.testclient import TestClient

from app.runner.setup import setup


@pytest.fixture
def http() -> TestClient:
    return TestClient(setup())


@pytest.fixture
def connection() -> Connection:
    return Connection(':memory:', check_same_thread=False)
