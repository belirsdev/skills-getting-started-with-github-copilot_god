"""Tests for FastAPI activities API using AAA pattern."""

import pytest


class TestGetActivities:
    """Test cases for GET /activities endpoint."""

    def test_get_all_activities(self, client):
        """Test retrieving all activities with their details."""
        # Arrange: No special setup needed

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Check response status and structure
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 10  # Should have 10 activities

        # Check structure of first activity (Chess Club)
        chess_club = data.get("Chess Club")
        assert chess_club is not None
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)


class TestSignup:
    """Test cases for POST /activities/{activity_name}/signup endpoint."""

    def test_valid_signup(self, client):
        """Test successful signup for an activity."""
        # Arrange: Choose an activity and email
        activity_name = "Chess Club"
        email = "student@example.com"

        # Act: Make POST request to signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Check success response
        assert response.status_code == 200
        data = response.json()
        assert data == {"message": f"Successfully signed up for {activity_name}"}

        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_duplicate_signup(self, client):
        """Test attempting to sign up for the same activity twice."""
        # Arrange: Sign up first time
        activity_name = "Programming Class"
        email = "student@example.com"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act: Attempt duplicate signup
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Should fail with 400
        assert response.status_code == 400
        data = response.json()
        assert data == {"detail": "Already signed up for this activity"}

    def test_signup_nonexistent_activity(self, client):
        """Test signing up for a non-existent activity."""
        # Arrange: Use invalid activity name
        activity_name = "Nonexistent Activity"
        email = "student@example.com"

        # Act: Make POST request
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert: Should fail with 404
        assert response.status_code == 404
        data = response.json()
        assert data == {"detail": "Activity not found"}

    def test_signup_full_activity(self, client):
        """Test signing up when activity is at maximum capacity."""
        # Arrange: Fill up an activity (Soccer Team has max 15)
        activity_name = "Soccer Team"
        max_participants = 15

        # Sign up max participants
        for i in range(max_participants):
            email = f"student{i}@example.com"
            client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act: Try to sign up one more
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "extra@example.com"}
        )

        # Assert: Should fail with 400
        assert response.status_code == 400
        data = response.json()
        assert data == {"detail": "Activity is full"}


class TestUnregister:
    """Test cases for DELETE /activities/{activity_name}/unregister endpoint."""

    def test_valid_unregister(self, client):
        """Test successful unregistration from an activity."""
        # Arrange: Sign up first
        activity_name = "Gym Class"
        email = "student@example.com"
        client.post(f"/activities/{activity_name}/signup", params={"email": email})

        # Act: Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert: Check success response
        assert response.status_code == 200
        data = response.json()
        assert data == {"message": f"Successfully unregistered from {activity_name}"}

        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_not_signed_up(self, client):
        """Test unregistering when not signed up."""
        # Arrange: Don't sign up first
        activity_name = "Basketball Club"
        email = "student@example.com"

        # Act: Try to unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert: Should fail with 400
        assert response.status_code == 400
        data = response.json()
        assert data == {"detail": "Not signed up for this activity"}

    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity."""
        # Arrange: Use invalid activity name
        activity_name = "Nonexistent Activity"
        email = "student@example.com"

        # Act: Make DELETE request
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert: Should fail with 404
        assert response.status_code == 404
        data = response.json()
        assert data == {"detail": "Activity not found"}