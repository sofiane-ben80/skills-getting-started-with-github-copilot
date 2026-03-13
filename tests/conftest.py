from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

_BASELINE_ACTIVITIES = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset in-memory activity state before and after each test."""
    activities.clear()
    activities.update(deepcopy(_BASELINE_ACTIVITIES))
    yield
    activities.clear()
    activities.update(deepcopy(_BASELINE_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)
