import os
import pytest
from fastapi.testclient import TestClient

from backend.db import init_db, get_db
from backend.seed import load_and_seed_content
from backend.main import app


@pytest.fixture
def test_db_path(tmp_path):
    db_file = tmp_path / "test_gyaan_loop.db"
    return str(db_file)


@pytest.fixture
def client(test_db_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", test_db_path)
    monkeypatch.setenv("AI_MOCK", "1")
    init_db(test_db_path)
    with get_db(test_db_path) as conn:
        load_and_seed_content(conn)

    with TestClient(app) as test_client:
        yield test_client
