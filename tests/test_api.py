from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    # Expect at least one known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "tester+signup@example.com"

    # Ensure email not already present
    if email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(email)

    # Signup
    signup_url = f"/activities/{quote(activity)}/signup?email={quote(email)}"
    res = client.post(signup_url)
    assert res.status_code == 200
    assert f"Signed up {email}" in res.json()["message"]

    # Verify participant added
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert email in data[activity]["participants"]

    # Signing up again should return 400
    res = client.post(signup_url)
    assert res.status_code == 400

    # Unregister
    delete_url = f"/activities/{quote(activity)}/participants?email={quote(email)}"
    res = client.delete(delete_url)
    assert res.status_code == 200
    assert f"Unregistered {email}" in res.json()["message"]

    # Verify participant removed
    res = client.get("/activities")
    data = res.json()
    assert email not in data[activity]["participants"]
