from .base_selenium_tests import BaseSeleniumTest, COMPLEX_PASSWORD
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tradeapp.models import Offer, User, Report, Message, Thread

class AdminTests(BaseSeleniumTest):
    def setUp(self):
        self.admin_user = self.create_test_user(username="adminuser", password=COMPLEX_PASSWORD, is_staff=True)
        self.regular_user = self.create_test_user(username="regularuser", password=COMPLEX_PASSWORD)
        self.login("adminuser", COMPLEX_PASSWORD)
        
        # Create test data for admin functions - make sure offer is approved
        self.offer = Offer.objects.create(
            title="Pending Offer",
            description="Pending approval",
            price=50.00,
            user=self.regular_user,
            status="approved"  # Changed from "pending" to "approved"
        )
        
        # Create a thread and message for reporting
        self.thread = Thread.objects.create(
            topic="Test Thread for Report",
            author=self.regular_user,
            offer=self.offer
        )
        self.message = Message.objects.create(
            thread=self.thread,
            author=self.regular_user,
            content="Test message that might be reported"
        )

    def test_review_offers_page(self):
        """Test accessing review offers page as staff"""
        self.driver.get(f"{self.live_server_url}/review-offers/")
        
        # Should see pending offers
        self.assertIn("review-offers", self.driver.current_url)

    def test_manage_users_page(self):
        """Test accessing manage users page"""
        self.driver.get(f"{self.live_server_url}/manage-users/")
        
        # Should see users list
        self.assertIn("manage-users", self.driver.current_url)

    def test_view_reports_page(self):
        """Test accessing reports page"""
        # Create a test report
        report = Report.objects.create(
            reported_message=self.message,
            reporter=self.regular_user,
            reason="spam",
            message="This is spam"
        )
        
        self.driver.get(f"{self.live_server_url}/admin/reports/")
        
        # Should see reports interface
        self.assertIn("reports", self.driver.current_url)