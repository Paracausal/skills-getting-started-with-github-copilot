import copy

from fastapi.testclient import TestClient
import pytest

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Snapshot and restore the in-memory activities to avoid test interference
    orig = copy.deepcopy(app_module.activities)
    yield
    app_module.activities.clear()
    app_module.activities.update(orig)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_duplicate():
    email = "tester@example.com"
    activity = "Chess Club"

    # Signup succeeds
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Duplicate signup should return 400
    r2 = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 400


def test_unregister():
    email = "remove_me@example.com"
    activity = "Programming Class"

    # Add participant
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert email in app_module.activities[activity]["participants"]

    # Remove participant
    r2 = client.delete(f"/activities/{activity}/signup", params={"email": email})
    assert r2.status_code == 200
    assert email not in app_module.activities[activity]["participants"]


def test_unregister_nonexistent():
    # Attempt to remove a non-existent participant
    r = client.delete(f"/activities/Chess%20Club/signup", params={"email": "nope@example.com"})
    assert r.status_code == 404
