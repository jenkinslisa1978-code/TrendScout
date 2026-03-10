"""
Newsletter Subscription API Tests
Tests for:
- POST /api/newsletter/subscribe - new email subscription
- POST /api/newsletter/subscribe - already subscribed email
- POST /api/newsletter/subscribe - invalid email (400)
- POST /api/newsletter/unsubscribe - unsubscribe email
- POTW cron task registration in APScheduler
"""

import pytest
import requests
import os
import random
import string
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

@pytest.fixture
def unique_email():
    """Generate a unique test email"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"TEST_newsletter_{random_suffix}@example.com"


class TestNewsletterSubscribe:
    """Test newsletter subscription endpoints"""
    
    def test_subscribe_valid_email(self, unique_email):
        """POST /api/newsletter/subscribe with valid email returns 'subscribed' status"""
        response = requests.post(
            f"{BASE_URL}/api/newsletter/subscribe",
            json={"email": unique_email},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert data.get("status") == "subscribed", f"Expected 'subscribed' status, got: {data}"
        assert data.get("email") == unique_email.lower()
    
    def test_subscribe_same_email_twice(self, unique_email):
        """POST /api/newsletter/subscribe with same email returns 'already_subscribed' status"""
        # First subscription
        response1 = requests.post(
            f"{BASE_URL}/api/newsletter/subscribe",
            json={"email": unique_email},
            headers={"Content-Type": "application/json"}
        )
        assert response1.status_code == 200
        
        # Second subscription with same email
        response2 = requests.post(
            f"{BASE_URL}/api/newsletter/subscribe",
            json={"email": unique_email},
            headers={"Content-Type": "application/json"}
        )
        assert response2.status_code == 200
        data = response2.json()
        assert data.get("status") == "already_subscribed", f"Expected 'already_subscribed', got: {data}"
    
    def test_subscribe_invalid_email_no_at(self):
        """POST /api/newsletter/subscribe with invalid email (no @) returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/newsletter/subscribe",
            json={"email": "invalidemail"},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    
    def test_subscribe_invalid_email_empty(self):
        """POST /api/newsletter/subscribe with empty email returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/newsletter/subscribe",
            json={"email": ""},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"
    
    def test_subscribe_invalid_email_whitespace(self):
        """POST /api/newsletter/subscribe with whitespace email returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/newsletter/subscribe",
            json={"email": "   "},
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 400, f"Expected 400, got {response.status_code}: {response.text}"


class TestNewsletterUnsubscribe:
    """Test newsletter unsubscription endpoints"""
    
    def test_unsubscribe_existing_email(self, unique_email):
        """POST /api/newsletter/unsubscribe with email returns 'unsubscribed' status"""
        # First subscribe
        sub_response = requests.post(
            f"{BASE_URL}/api/newsletter/subscribe",
            json={"email": unique_email},
            headers={"Content-Type": "application/json"}
        )
        assert sub_response.status_code == 200
        
        # Then unsubscribe
        unsub_response = requests.post(
            f"{BASE_URL}/api/newsletter/unsubscribe",
            json={"email": unique_email},
            headers={"Content-Type": "application/json"}
        )
        
        assert unsub_response.status_code == 200, f"Expected 200, got {unsub_response.status_code}: {unsub_response.text}"
        data = unsub_response.json()
        assert data.get("status") == "unsubscribed", f"Expected 'unsubscribed' status, got: {data}"
    
    def test_unsubscribe_resubscribe(self, unique_email):
        """After unsubscribe, re-subscribe returns 'resubscribed' status"""
        # Subscribe
        requests.post(
            f"{BASE_URL}/api/newsletter/subscribe",
            json={"email": unique_email},
            headers={"Content-Type": "application/json"}
        )
        
        # Unsubscribe
        requests.post(
            f"{BASE_URL}/api/newsletter/unsubscribe",
            json={"email": unique_email},
            headers={"Content-Type": "application/json"}
        )
        
        # Re-subscribe
        resub_response = requests.post(
            f"{BASE_URL}/api/newsletter/subscribe",
            json={"email": unique_email},
            headers={"Content-Type": "application/json"}
        )
        
        assert resub_response.status_code == 200
        data = resub_response.json()
        assert data.get("status") == "resubscribed", f"Expected 'resubscribed' status, got: {data}"


class TestPOTWCronTask:
    """Test Product of the Week cron task registration"""
    
    def test_potw_task_registered(self):
        """Verify 'send_product_of_the_week' task is registered in APScheduler"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/status",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        # Check available_tasks includes send_product_of_the_week
        available_tasks = data.get("available_tasks", {})
        assert "send_product_of_the_week" in available_tasks, f"Task 'send_product_of_the_week' not found in registered tasks: {list(available_tasks.keys())}"
    
    def test_potw_task_schedule(self):
        """Verify 'send_product_of_the_week' task has schedule '0 11 * * 3' (Wednesday 11 AM UTC)"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/status",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        available_tasks = data.get("available_tasks", {})
        potw_task = available_tasks.get("send_product_of_the_week", {})
        
        expected_schedule = "0 11 * * 3"
        actual_schedule = potw_task.get("default_schedule")
        
        assert actual_schedule == expected_schedule, f"Expected schedule '{expected_schedule}', got '{actual_schedule}'"
    
    def test_potw_task_description(self):
        """Verify 'send_product_of_the_week' task has proper description"""
        response = requests.get(
            f"{BASE_URL}/api/jobs/status",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        available_tasks = data.get("available_tasks", {})
        potw_task = available_tasks.get("send_product_of_the_week", {})
        
        description = potw_task.get("description", "")
        assert "Product of the Week" in description, f"Expected description to contain 'Product of the Week', got: {description}"


class TestHealthCheck:
    """Basic health check"""
    
    def test_api_health(self):
        """API health check passes"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
