import pytest

from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    endpoint = "/"

    # Act
    response = client.get(endpoint, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape(client):
    # Arrange
    endpoint = "/activities"

    # Act
    response = client.get(endpoint)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Basketball Team" in payload
    assert "participants" in payload["Basketball Team"]
    assert isinstance(payload["Basketball Team"]["participants"], list)


def test_signup_succeeds_for_valid_activity_and_email(client):
    # Arrange
    endpoint = "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up newstudent@mergington.edu for Chess Club"
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_student(client):
    # Arrange
    endpoint = "/activities/Chess%20Club/signup?email=michael@mergington.edu"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_rejects_unknown_activity(client):
    # Arrange
    endpoint = "/activities/Unknown%20Activity/signup?email=student@mergington.edu"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_requires_email_query_parameter(client):
    # Arrange
    endpoint = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 422


def test_unregister_succeeds_for_enrolled_student(client):
    # Arrange
    endpoint = "/activities/Basketball%20Team/signup?email=liam@mergington.edu"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered liam@mergington.edu from Basketball Team"
    assert "liam@mergington.edu" not in activities["Basketball Team"]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    endpoint = "/activities/Unknown%20Activity/signup?email=student@mergington.edu"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_rejects_student_not_signed_up(client):
    # Arrange
    endpoint = "/activities/Basketball%20Team/signup?email=notenrolled@mergington.edu"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_unregister_requires_email_query_parameter(client):
    # Arrange
    endpoint = "/activities/Basketball%20Team/signup"

    # Act
    response = client.delete(endpoint)

    # Assert
    assert response.status_code == 422


def test_signup_then_unregister_flow(client):
    # Arrange
    signup_endpoint = "/activities/Art%20Club/signup?email=flowstudent@mergington.edu"
    unregister_endpoint = "/activities/Art%20Club/signup?email=flowstudent@mergington.edu"

    # Act
    signup_response = client.post(signup_endpoint)
    unregister_response = client.delete(unregister_endpoint)

    # Assert
    assert signup_response.status_code == 200
    assert unregister_response.status_code == 200
    assert "flowstudent@mergington.edu" not in activities["Art Club"]["participants"]


@pytest.mark.xfail(reason="max_participants limit is not enforced yet")
def test_signup_rejects_when_activity_is_full(client):
    # Arrange
    activities["Full Activity"] = {
        "description": "Capacity test activity",
        "schedule": "Mondays, 7:00 AM - 8:00 AM",
        "max_participants": 1,
        "participants": ["full@mergington.edu"],
    }
    endpoint = "/activities/Full%20Activity/signup?email=extra@mergington.edu"

    # Act
    response = client.post(endpoint)

    # Assert
    assert response.status_code == 400
