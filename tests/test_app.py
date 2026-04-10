"""
Tests for the Mergington High School API

Uses the AAA (Arrange-Act-Assert) pattern to structure each test clearly.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Fixture to restore the in-memory activities state before and after each test.
    
    This prevents test pollution where one test's modifications affect another.
    Uses deep copy to preserve the original structure.
    """
    # Arrange: Save the original state
    original_activities = copy.deepcopy(activities)
    
    yield
    
    # Cleanup: Restore the original state
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the app."""
    return TestClient(app)


class TestGetActivities:
    """Tests for the GET /activities endpoint."""
    
    def test_get_all_activities_returns_correct_structure(self, client):
        """Test that GET /activities returns all activities with correct data."""
        # Arrange (already set up by fixture)
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert len(data) == 9  # All 9 activities
    
    def test_activity_contains_required_fields(self, client):
        """Test that each activity has the required fields."""
        # Arrange (already set up by fixture)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        # Assert
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_participants_list_contains_initial_data(self, client):
        """Test that participants list contains the initial data."""
        # Arrange (already set up by fixture)
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_successfully_adds_participant(self, client):
        """Test that signup successfully adds a new participant to an activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant was added
        check_response = client.get("/activities")
        assert email in check_response.json()["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signup for a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_duplicate_signup_returns_400(self, client):
        """Test that signing up the same student twice returns 400."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]


class TestUnregister:
    """Tests for the DELETE /activities/{activity_name}/participants/{email} endpoint."""
    
    def test_unregister_successfully_removes_participant(self, client):
        """Test that unregistering successfully removes a participant."""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        
        # Verify participant was removed
        check_response = client.get("/activities")
        assert email not in check_response.json()["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_participant_returns_404(self, client):
        """Test that unregistering a non-existent participant returns 404."""
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found"
    
    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a non-existent activity returns 404."""
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity_name}/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"