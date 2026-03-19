"""
Test suite for Reports API endpoints

Tests the Market Intelligence Reports feature including:
- GET /api/reports/ - list reports
- GET /api/reports/weekly-winning-products - latest weekly report
- GET /api/reports/monthly-market-trends - latest monthly report
- GET /api/reports/public/weekly-winning-products - public preview
- GET /api/reports/public/monthly-market-trends - public preview
- GET /api/reports/history/{report_type} - historical reports
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://uk-seller-hub-1.preview.emergentagent.com').rstrip('/')
DEMO_AUTH_TOKEN = "Bearer demo_demo-user-id"


class TestHealthEndpoint:
    """Test API health endpoint"""
    
    def test_health_check(self):
        """Test health endpoint returns healthy status"""
        response = requests.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")


class TestReportsListEndpoint:
    """Test GET /api/reports/ endpoint"""
    
    def test_get_reports_list_success(self):
        """Test getting list of reports"""
        response = requests.get(f"{BASE_URL}/api/reports/")
        assert response.status_code == 200
        
        data = response.json()
        assert "reports" in data
        assert "count" in data
        assert "latest" in data
        assert isinstance(data["reports"], list)
        print(f"✓ Reports list returned {data['count']} reports")
    
    def test_reports_list_contains_latest_refs(self):
        """Test that reports list includes latest weekly/monthly references"""
        response = requests.get(f"{BASE_URL}/api/reports/")
        assert response.status_code == 200
        
        data = response.json()
        latest = data["latest"]
        
        # Should have weekly and monthly references (may be None if no reports yet)
        assert "weekly" in latest
        assert "monthly" in latest
        print("✓ Reports list contains latest references")
    
    def test_reports_list_with_type_filter(self):
        """Test filtering reports by type"""
        response = requests.get(f"{BASE_URL}/api/reports/?report_type=weekly_winning_products")
        assert response.status_code == 200
        
        data = response.json()
        # If reports exist, they should all be of the filtered type
        for report in data["reports"]:
            assert report["metadata"]["report_type"] == "weekly_winning_products"
        print("✓ Reports list filtering by type works")


class TestWeeklyReportEndpoint:
    """Test GET /api/reports/weekly-winning-products endpoint"""
    
    def test_get_weekly_report_success(self):
        """Test getting latest weekly report"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        assert "report" in data
        assert "user_plan" in data
        assert "is_authenticated" in data
        print("✓ Weekly report endpoint returns data")
    
    def test_weekly_report_structure(self):
        """Test weekly report has proper structure"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        # Check metadata
        assert "metadata" in report
        metadata = report["metadata"]
        assert metadata["report_type"] == "weekly_winning_products"
        assert "title" in metadata
        assert "slug" in metadata
        print(f"✓ Weekly report: {metadata.get('title')}")
    
    def test_weekly_report_has_sections(self):
        """Test weekly report has sections"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        assert "sections" in report
        assert isinstance(report["sections"], list)
        assert len(report["sections"]) > 0
        
        # Check expected sections
        section_titles = [s["title"] for s in report["sections"]]
        assert "Trend Stage Analysis" in section_titles  # Free section
        assert "Competition Analysis" in section_titles  # Free section
        print(f"✓ Weekly report has {len(report['sections'])} sections")
    
    def test_weekly_report_free_sections_unlocked(self):
        """Test free sections are accessible without auth"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        # Find trend stage analysis section (should be free)
        trend_section = next((s for s in report["sections"] if s["title"] == "Trend Stage Analysis"), None)
        assert trend_section is not None
        assert trend_section.get("locked") is not True
        assert "data" in trend_section
        print("✓ Free sections are accessible without auth")
    
    def test_weekly_report_pro_sections_locked_for_free_user(self):
        """Test Pro sections are locked for unauthenticated users"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        # Find top 20 products section (should be pro only)
        top_products_section = next((s for s in report["sections"] if "Top 20" in s["title"]), None)
        assert top_products_section is not None
        assert top_products_section.get("locked") == True
        assert "unlock_message" in top_products_section
        print("✓ Pro sections are locked for free users")
    
    def test_weekly_report_has_summary(self):
        """Test weekly report has summary data"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        assert "summary" in report
        summary = report["summary"]
        assert "total_products_analyzed" in summary
        assert "avg_success_probability" in summary
        assert "low_competition_opportunities" in summary
        print(f"✓ Weekly report analyzed {summary.get('total_products_analyzed')} products")


class TestMonthlyReportEndpoint:
    """Test GET /api/reports/monthly-market-trends endpoint"""
    
    def test_get_monthly_report_success(self):
        """Test getting latest monthly report"""
        response = requests.get(f"{BASE_URL}/api/reports/monthly-market-trends")
        assert response.status_code == 200
        
        data = response.json()
        assert "report" in data
        assert "user_plan" in data
        assert "is_authenticated" in data
        print("✓ Monthly report endpoint returns data")
    
    def test_monthly_report_structure(self):
        """Test monthly report has proper structure"""
        response = requests.get(f"{BASE_URL}/api/reports/monthly-market-trends")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        # Check metadata
        assert "metadata" in report
        metadata = report["metadata"]
        assert metadata["report_type"] == "monthly_market_trends"
        assert "title" in metadata
        assert "slug" in metadata
        print(f"✓ Monthly report: {metadata.get('title')}")
    
    def test_monthly_report_has_sections(self):
        """Test monthly report has sections"""
        response = requests.get(f"{BASE_URL}/api/reports/monthly-market-trends")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        assert "sections" in report
        assert isinstance(report["sections"], list)
        assert len(report["sections"]) > 0
        
        # Check expected sections
        section_titles = [s["title"] for s in report["sections"]]
        assert "Emerging Product Categories" in section_titles  # Free section
        assert "Demand vs Competition Analysis" in section_titles  # Free section
        print(f"✓ Monthly report has {len(report['sections'])} sections")
    
    def test_monthly_report_emerging_categories(self):
        """Test monthly report has emerging categories data"""
        response = requests.get(f"{BASE_URL}/api/reports/monthly-market-trends")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        # Find emerging categories section
        emerging_section = next((s for s in report["sections"] if "Emerging" in s["title"]), None)
        assert emerging_section is not None
        assert emerging_section.get("locked") is not True
        
        # Check data structure
        section_data = emerging_section.get("data", {})
        assert "categories" in section_data
        print(f"✓ Monthly report has {len(section_data.get('categories', []))} emerging categories")
    
    def test_monthly_report_has_market_health(self):
        """Test monthly report includes market health assessment"""
        response = requests.get(f"{BASE_URL}/api/reports/monthly-market-trends")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        assert "summary" in report
        summary = report["summary"]
        assert "market_health" in summary
        
        market_health = summary["market_health"]
        assert "status" in market_health
        assert "growing_categories" in market_health
        print(f"✓ Market health status: {market_health.get('status')}")


class TestPublicWeeklyReportEndpoint:
    """Test GET /api/reports/public/weekly-winning-products endpoint"""
    
    def test_get_public_weekly_report_success(self):
        """Test getting public weekly report preview"""
        response = requests.get(f"{BASE_URL}/api/reports/public/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        assert "report" in data
        assert "cta" in data
        print("✓ Public weekly report endpoint returns data")
    
    def test_public_weekly_report_has_top_5_products(self):
        """Test public preview has top 5 products"""
        response = requests.get(f"{BASE_URL}/api/reports/public/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        assert "public_preview" in report
        preview = report["public_preview"]
        assert "top_5_products" in preview
        
        products = preview["top_5_products"]
        assert isinstance(products, list)
        assert len(products) <= 5
        print(f"✓ Public preview has {len(products)} top products")
    
    def test_public_weekly_report_has_locked_margin_details(self):
        """Test public preview has locked margin details"""
        response = requests.get(f"{BASE_URL}/api/reports/public/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        preview = report["public_preview"]
        products = preview["top_5_products"]
        
        # Check that margin is locked
        for product in products:
            margin = product.get("estimated_margin")
            assert margin == "Unlock for details" or isinstance(margin, (int, float))
        print("✓ Public preview has locked margin details")
    
    def test_public_weekly_report_has_cta(self):
        """Test public report has call-to-action"""
        response = requests.get(f"{BASE_URL}/api/reports/public/weekly-winning-products")
        assert response.status_code == 200
        
        data = response.json()
        cta = data["cta"]
        
        assert "message" in cta
        assert "action" in cta
        assert "url" in cta
        print(f"✓ CTA: {cta.get('action')}")


class TestPublicMonthlyReportEndpoint:
    """Test GET /api/reports/public/monthly-market-trends endpoint"""
    
    def test_get_public_monthly_report_success(self):
        """Test getting public monthly report preview"""
        response = requests.get(f"{BASE_URL}/api/reports/public/monthly-market-trends")
        assert response.status_code == 200
        
        data = response.json()
        assert "report" in data
        assert "cta" in data
        print("✓ Public monthly report endpoint returns data")
    
    def test_public_monthly_report_has_top_3_emerging(self):
        """Test public preview has top 3 emerging categories"""
        response = requests.get(f"{BASE_URL}/api/reports/public/monthly-market-trends")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        
        assert "public_preview" in report
        preview = report["public_preview"]
        assert "top_3_emerging" in preview
        
        categories = preview["top_3_emerging"]
        assert isinstance(categories, list)
        assert len(categories) <= 3
        print(f"✓ Public preview has {len(categories)} emerging categories")
    
    def test_public_monthly_report_has_market_snapshot(self):
        """Test public preview has market snapshot"""
        response = requests.get(f"{BASE_URL}/api/reports/public/monthly-market-trends")
        assert response.status_code == 200
        
        data = response.json()
        report = data["report"]
        preview = report["public_preview"]
        
        assert "market_snapshot" in preview
        snapshot = preview["market_snapshot"]
        assert "total_categories" in snapshot
        assert "growing_categories" in snapshot
        print(f"✓ Market snapshot shows {snapshot.get('total_categories')} categories")


class TestReportHistoryEndpoint:
    """Test GET /api/reports/history/{report_type} endpoint"""
    
    def test_get_weekly_history_success(self):
        """Test getting weekly report history"""
        response = requests.get(f"{BASE_URL}/api/reports/history/weekly_winning_products")
        assert response.status_code == 200
        
        data = response.json()
        assert "reports" in data
        assert "count" in data
        assert "user_plan" in data
        print(f"✓ Weekly history returns {data['count']} reports")
    
    def test_get_monthly_history_success(self):
        """Test getting monthly report history"""
        response = requests.get(f"{BASE_URL}/api/reports/history/monthly_market_trends")
        assert response.status_code == 200
        
        data = response.json()
        assert "reports" in data
        assert "count" in data
        assert "user_plan" in data
        print(f"✓ Monthly history returns {data['count']} reports")
    
    def test_invalid_report_type_returns_400(self):
        """Test invalid report type returns 400 error"""
        response = requests.get(f"{BASE_URL}/api/reports/history/invalid_type")
        assert response.status_code == 400
        print("✓ Invalid report type returns 400")
    
    def test_history_limit_for_free_user(self):
        """Test free users have limited history access"""
        response = requests.get(f"{BASE_URL}/api/reports/history/weekly_winning_products")
        assert response.status_code == 200
        
        data = response.json()
        # Free users should be limited to 3 reports
        assert data["user_plan"] == "free"
        assert data["count"] <= 3
        print(f"✓ Free user history limited to {data['count']} reports")


class TestAuthenticatedReportAccess:
    """Test report access with authentication"""
    
    def test_authenticated_weekly_report_access(self):
        """Test authenticated access to weekly report"""
        headers = {"Authorization": DEMO_AUTH_TOKEN}
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_authenticated"] == True
        print("✓ Authenticated weekly report access works")
    
    def test_authenticated_monthly_report_access(self):
        """Test authenticated access to monthly report"""
        headers = {"Authorization": DEMO_AUTH_TOKEN}
        response = requests.get(f"{BASE_URL}/api/reports/monthly-market-trends", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_authenticated"] == True
        print("✓ Authenticated monthly report access works")


# Fixtures
@pytest.fixture(scope="session")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
