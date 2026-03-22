"""
Test automation and ingestion endpoints for TrendScout admin automation.
Tests the fix for CSRF handling and response.json() body stream issues.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestAutomationEndpoints:
    """Test /api/automation/* endpoints"""
    
    def test_automation_run_full_pipeline(self):
        """POST /api/automation/run with job_type full_pipeline returns success"""
        response = requests.post(
            f"{BASE_URL}/api/automation/run",
            json={"job_type": "full_pipeline"},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "success" in data, f"Response missing 'success' field: {data}"
        assert data["success"] == True, f"Expected success=True, got {data}"
        print(f"✓ Automation run full_pipeline: processed={data.get('processed', 0)}, alerts={data.get('alerts_generated', 0)}")
    
    def test_automation_logs(self):
        """GET /api/automation/logs returns data array"""
        response = requests.get(f"{BASE_URL}/api/automation/logs")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "data" in data, f"Response missing 'data' field: {data}"
        assert isinstance(data["data"], list), f"Expected data to be a list: {data}"
        print(f"✓ Automation logs: {len(data['data'])} logs returned")
    
    def test_automation_stats(self):
        """GET /api/automation/stats returns stats"""
        response = requests.get(f"{BASE_URL}/api/automation/stats")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Check expected fields
        expected_fields = ["total_runs", "success_rate", "products_processed", "alerts_generated"]
        for field in expected_fields:
            assert field in data, f"Response missing '{field}' field: {data}"
        print(f"✓ Automation stats: total_runs={data.get('total_runs')}, success_rate={data.get('success_rate')}%")


class TestIngestionEndpoints:
    """Test /api/ingestion/* endpoints"""
    
    def test_ingestion_amazon(self):
        """POST /api/ingestion/amazon with limit 5 returns success"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/amazon",
            json={"limit": 5},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        # Check for success or expected fields
        assert "fetched" in data or "success" in data, f"Response missing expected fields: {data}"
        print(f"✓ Amazon import: fetched={data.get('fetched', 0)}, inserted={data.get('inserted', 0)}, updated={data.get('updated', 0)}")
    
    def test_ingestion_tiktok(self):
        """POST /api/ingestion/tiktok with limit 5 returns success"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/tiktok",
            json={"limit": 5},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "fetched" in data or "success" in data, f"Response missing expected fields: {data}"
        print(f"✓ TikTok import: fetched={data.get('fetched', 0)}, inserted={data.get('inserted', 0)}, updated={data.get('updated', 0)}")
    
    def test_ingestion_supplier(self):
        """POST /api/ingestion/supplier with limit 5 returns success"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/supplier",
            json={"limit": 5},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "fetched" in data or "success" in data, f"Response missing expected fields: {data}"
        print(f"✓ Supplier import: fetched={data.get('fetched', 0)}, inserted={data.get('inserted', 0)}, updated={data.get('updated', 0)}")
    
    def test_ingestion_full_sync(self):
        """POST /api/ingestion/full-sync with limit 5 returns success"""
        response = requests.post(
            f"{BASE_URL}/api/ingestion/full-sync",
            json={"limit": 5},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "success" in data, f"Response missing 'success' field: {data}"
        assert data["success"] == True, f"Expected success=True, got {data}"
        print(f"✓ Full sync: total_imported={data.get('total_imported', 0)}, total_alerts={data.get('total_alerts', 0)}")
    
    def test_ingestion_sources(self):
        """GET /api/ingestion/sources returns available sources"""
        response = requests.get(f"{BASE_URL}/api/ingestion/sources")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "sources" in data, f"Response missing 'sources' field: {data}"
        assert isinstance(data["sources"], list), f"Expected sources to be a list: {data}"
        assert len(data["sources"]) >= 3, f"Expected at least 3 sources, got {len(data['sources'])}"
        print(f"✓ Ingestion sources: {len(data['sources'])} sources available")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
