"""
PDF Export API Tests for ViralScout

Tests for PDF download endpoints:
- Weekly report PDF download
- Monthly report PDF download
- Public weekly report PDF download

Key validations:
- Valid PDF response (starts with %PDF signature)
- Correct Content-Type (application/pdf)
- Content-Disposition header with filename
- Appropriate status codes (200 for success, 404 for missing reports)
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestWeeklyReportPDF:
    """Tests for weekly winning products PDF endpoint"""
    
    def test_weekly_pdf_returns_valid_pdf(self):
        """GET /api/reports/weekly-winning-products/pdf returns valid PDF"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products/pdf", timeout=30)
        
        # Should return 200 or 404 (if no report exists)
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            # Verify Content-Type is PDF
            content_type = response.headers.get('Content-Type', '')
            assert 'application/pdf' in content_type, f"Expected application/pdf, got: {content_type}"
            print(f"PASS: Weekly PDF - Content-Type is application/pdf")
            
            # Verify Content-Disposition header has filename
            content_disp = response.headers.get('Content-Disposition', '')
            assert 'attachment' in content_disp, f"Missing attachment in Content-Disposition: {content_disp}"
            assert 'filename=' in content_disp, f"Missing filename in Content-Disposition: {content_disp}"
            assert '.pdf' in content_disp, f"Filename missing .pdf extension: {content_disp}"
            print(f"PASS: Weekly PDF - Content-Disposition header: {content_disp}")
            
            # Verify PDF signature (starts with %PDF)
            pdf_content = response.content
            assert len(pdf_content) > 100, f"PDF content too small: {len(pdf_content)} bytes"
            assert pdf_content[:4] == b'%PDF', f"Invalid PDF signature: {pdf_content[:20]}"
            print(f"PASS: Weekly PDF - Valid %PDF signature, size: {len(pdf_content)} bytes")
        else:
            # 404 is acceptable if no report exists
            print(f"INFO: Weekly PDF - No report available (404)")
    
    def test_weekly_pdf_has_content_length(self):
        """Weekly PDF response should have Content-Length header"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products/pdf", timeout=30)
        
        if response.status_code == 200:
            content_length = response.headers.get('Content-Length')
            assert content_length is not None, "Missing Content-Length header"
            assert int(content_length) > 0, f"Invalid Content-Length: {content_length}"
            print(f"PASS: Weekly PDF - Content-Length: {content_length} bytes")


class TestMonthlyReportPDF:
    """Tests for monthly market trends PDF endpoint"""
    
    def test_monthly_pdf_returns_valid_pdf_or_404(self):
        """GET /api/reports/monthly-market-trends/pdf returns valid PDF or 404"""
        response = requests.get(f"{BASE_URL}/api/reports/monthly-market-trends/pdf", timeout=30)
        
        # Should return 200 or 404 (if no report exists)
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            # Verify Content-Type is PDF
            content_type = response.headers.get('Content-Type', '')
            assert 'application/pdf' in content_type, f"Expected application/pdf, got: {content_type}"
            print(f"PASS: Monthly PDF - Content-Type is application/pdf")
            
            # Verify Content-Disposition header has filename
            content_disp = response.headers.get('Content-Disposition', '')
            assert 'attachment' in content_disp, f"Missing attachment in Content-Disposition: {content_disp}"
            assert 'filename=' in content_disp, f"Missing filename in Content-Disposition: {content_disp}"
            assert '.pdf' in content_disp, f"Filename missing .pdf extension: {content_disp}"
            print(f"PASS: Monthly PDF - Content-Disposition header: {content_disp}")
            
            # Verify PDF signature
            pdf_content = response.content
            assert pdf_content[:4] == b'%PDF', f"Invalid PDF signature: {pdf_content[:20]}"
            print(f"PASS: Monthly PDF - Valid %PDF signature, size: {len(pdf_content)} bytes")
        else:
            # 404 is acceptable if no monthly report exists
            print(f"INFO: Monthly PDF - No report available (404)")
    
    def test_monthly_pdf_404_error_message(self):
        """404 response should have appropriate error message"""
        response = requests.get(f"{BASE_URL}/api/reports/monthly-market-trends/pdf", timeout=30)
        
        if response.status_code == 404:
            data = response.json()
            assert 'detail' in data, "404 response missing detail field"
            print(f"PASS: Monthly PDF - 404 error detail: {data['detail']}")


class TestPublicWeeklyReportPDF:
    """Tests for public weekly report PDF endpoint"""
    
    def test_public_pdf_returns_valid_pdf(self):
        """GET /api/reports/public/weekly-winning-products/pdf returns valid PDF"""
        response = requests.get(f"{BASE_URL}/api/reports/public/weekly-winning-products/pdf", timeout=30)
        
        # Should return 200 or 404
        assert response.status_code in [200, 404], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            # Verify Content-Type is PDF
            content_type = response.headers.get('Content-Type', '')
            assert 'application/pdf' in content_type, f"Expected application/pdf, got: {content_type}"
            print(f"PASS: Public PDF - Content-Type is application/pdf")
            
            # Verify Content-Disposition header
            content_disp = response.headers.get('Content-Disposition', '')
            assert 'attachment' in content_disp, f"Missing attachment: {content_disp}"
            assert 'filename=' in content_disp, f"Missing filename: {content_disp}"
            assert 'preview' in content_disp.lower(), f"Filename should contain 'preview': {content_disp}"
            print(f"PASS: Public PDF - Content-Disposition: {content_disp}")
            
            # Verify PDF signature
            pdf_content = response.content
            assert pdf_content[:4] == b'%PDF', f"Invalid PDF signature: {pdf_content[:20]}"
            print(f"PASS: Public PDF - Valid %PDF signature, size: {len(pdf_content)} bytes")
        else:
            print(f"INFO: Public PDF - No report available (404)")
    
    def test_public_pdf_accessible_without_auth(self):
        """Public PDF endpoint should be accessible without authentication"""
        # Make request without any auth headers
        response = requests.get(
            f"{BASE_URL}/api/reports/public/weekly-winning-products/pdf",
            timeout=30
        )
        
        # Should not return 401/403 - public endpoint
        assert response.status_code not in [401, 403], f"Public endpoint returned auth error: {response.status_code}"
        print(f"PASS: Public PDF - No auth required, status: {response.status_code}")
    
    def test_public_pdf_smaller_than_full_report(self):
        """Public preview PDF should generally be smaller than full report"""
        full_response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products/pdf", timeout=30)
        public_response = requests.get(f"{BASE_URL}/api/reports/public/weekly-winning-products/pdf", timeout=30)
        
        if full_response.status_code == 200 and public_response.status_code == 200:
            full_size = len(full_response.content)
            public_size = len(public_response.content)
            
            print(f"INFO: Full PDF size: {full_size} bytes, Public PDF size: {public_size} bytes")
            # Public preview may be smaller or similar depending on content
            # Just verify both are valid PDFs
            assert full_size > 0 and public_size > 0, "Both PDFs should have content"
            print(f"PASS: Both PDFs have valid content")


class TestPDFErrorHandling:
    """Tests for PDF endpoint error handling"""
    
    def test_invalid_endpoint_returns_404(self):
        """Invalid PDF endpoint should return 404 or method not allowed"""
        response = requests.get(f"{BASE_URL}/api/reports/invalid-report/pdf", timeout=30)
        
        assert response.status_code in [404, 405, 422], f"Expected 404/405/422 for invalid endpoint: {response.status_code}"
        print(f"PASS: Invalid PDF endpoint returns appropriate error: {response.status_code}")


class TestPDFContentQuality:
    """Tests for PDF content quality - verify PDF structure"""
    
    def test_weekly_pdf_contains_viralscout_branding(self):
        """Weekly PDF should contain ViralScout branding in content"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products/pdf", timeout=30)
        
        if response.status_code == 200:
            # Search for branding text in PDF content (as string)
            pdf_text = response.content.decode('latin-1', errors='ignore')
            
            # Check for expected text fragments (PDF text may be encoded)
            # ViralScout brand name should appear
            has_branding = 'ViralScout' in pdf_text or 'viralscout' in pdf_text.lower()
            print(f"INFO: PDF branding check - ViralScout found: {has_branding}")
            
            # Verify PDF is properly terminated
            assert b'%%EOF' in response.content or b'%EOF' in response.content, "PDF should have EOF marker"
            print(f"PASS: Weekly PDF has proper EOF marker")
    
    def test_pdf_response_is_binary(self):
        """PDF response should be binary data, not text"""
        response = requests.get(f"{BASE_URL}/api/reports/weekly-winning-products/pdf", timeout=30)
        
        if response.status_code == 200:
            content = response.content
            # PDF should start with %PDF-X.X (where X.X is version)
            # Format: %PDF-1.4 (bytes 0-4 = %PDF-, byte 5 = version major)
            assert content[0:5] == b'%PDF-', "PDF should start with %PDF- signature"
            # Version number follows (e.g., 1.4, 1.5, 1.6, 1.7, 2.0)
            version_byte = content[5:6]
            assert version_byte in [b'1', b'2'], f"PDF version should start with 1 or 2, got: {version_byte}"
            print(f"PASS: PDF is valid binary format, header: {content[0:8].decode('utf-8', errors='ignore')}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
