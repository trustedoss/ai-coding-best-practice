import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from app import app as flask_app  # noqa: E402


@pytest.fixture
def client():
    flask_app.config.update(TESTING=True)
    with flask_app.test_client() as client:
        yield client
