"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team and practice",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 8,
            "participants": ["jordan@mergington.edu", "casey@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and improve acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["avery@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and various art techniques",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["morgan@mergington.edu", "riley@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 10,
            "participants": ["taylor@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore scientific experiments and discoveries",
            "schedule": "Fridays, 4:00 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["jordan@mergington.edu", "alex@mergington.edu"]
        }
    }
    
    # Clear and reset activities
    activities.clear()
    activities.update(original_activities)
    yield
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


# Tests for /activities endpoint
def test_get_activities(client, reset_activities):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert len(data) == 9


def test_get_activities_returns_correct_structure(client, reset_activities):
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    data = response.json()
    activity = data["Chess Club"]
    
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


# Tests for /signup endpoint
def test_signup_for_activity_success(client, reset_activities):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    
    # Verify student was added
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_for_nonexistent_activity(client, reset_activities):
    """Test signup for activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_signup_already_registered(client, reset_activities):
    """Test signup for activity when already registered"""
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up"


def test_signup_multiple_different_activities(client, reset_activities):
    """Test signing up for multiple different activities"""
    email = "versatile@mergington.edu"
    
    # Sign up for Chess Club
    response1 = client.post(
        f"/activities/Chess Club/signup?email={email}"
    )
    assert response1.status_code == 200
    assert email in activities["Chess Club"]["participants"]
    
    # Sign up for Programming Class
    response2 = client.post(
        f"/activities/Programming Class/signup?email={email}"
    )
    assert response2.status_code == 200
    assert email in activities["Programming Class"]["participants"]


# Tests for /unregister endpoint
def test_unregister_from_activity_success(client, reset_activities):
    """Test successful unregister from an activity"""
    response = client.post(
        "/activities/Chess Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # Verify student was removed
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_from_nonexistent_activity(client, reset_activities):
    """Test unregister from activity that doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"


def test_unregister_not_registered(client, reset_activities):
    """Test unregister for a student not registered"""
    response = client.post(
        "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student not found in activity"


def test_signup_then_unregister(client, reset_activities):
    """Test signing up and then unregistering"""
    email = "temporary@mergington.edu"
    activity = "Chess Club"
    
    # Sign up
    response1 = client.post(
        f"/activities/{activity}/signup?email={email}"
    )
    assert response1.status_code == 200
    assert email in activities[activity]["participants"]
    
    # Unregister
    response2 = client.post(
        f"/activities/{activity}/unregister?email={email}"
    )
    assert response2.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_multiple_participants_only_removes_one(client, reset_activities):
    """Test that unregistering one student doesn't affect others"""
    activity = "Chess Club"
    original_participants = activities[activity]["participants"].copy()
    
    # Unregister one participant
    response = client.post(
        f"/activities/{activity}/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    
    # Check that other participants are still there
    assert "daniel@mergington.edu" in activities[activity]["participants"]
    
    # Check that the removed participant is gone
    assert "michael@mergington.edu" not in activities[activity]["participants"]
    
    # Check that exactly one was removed
    assert len(activities[activity]["participants"]) == len(original_participants) - 1


def test_participant_count_updates(client, reset_activities):
    """Test that participant count in activities updates correctly"""
    response1 = client.get("/activities")
    data1 = response1.json()
    initial_count = len(data1["Chess Club"]["participants"])
    
    # Sign up a new participant
    client.post("/activities/Chess Club/signup?email=newparticipant@mergington.edu")
    
    response2 = client.get("/activities")
    data2 = response2.json()
    new_count = len(data2["Chess Club"]["participants"])
    
    assert new_count == initial_count + 1
