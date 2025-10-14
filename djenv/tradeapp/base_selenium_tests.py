from django.test import LiveServerTestCase, override_settings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from django.contrib.auth.models import User
from tradeapp.models import Profile, Offer
import time
import os

# Complex passwords that won't trigger browser security warnings
COMPLEX_PASSWORD = "TestPass123!@#"
COMPLEX_PASSWORD_2 = "ComplexPass456$%^"

# Completely disable static files during tests
@override_settings(
    DEBUG=False,
    STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage',
    WHITENOISE_AUTOREFRESH=True
)
class BaseSeleniumTest(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = webdriver.ChromeOptions()
        # Add these options to prevent password security warnings
        chrome_options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False
        })
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        cls.driver.implicitly_wait(10)
        cls.wait = WebDriverWait(cls.driver, 15)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def login(self, username="testuser", password=COMPLEX_PASSWORD):
        """Helper method to login user"""
        self.driver.get(f"{self.live_server_url}/login")
        
        username_field = self.driver.find_element(By.NAME, "username")
        password_field = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        
        # Wait for login to complete - handle both possible redirects
        try:
            self.wait.until(EC.url_contains("/home"))
        except:
            # Sometimes it might redirect to different page
            self.wait.until(lambda driver: "login" not in driver.current_url)

    def logout(self):
        """Helper method to logout user"""
        try:
            logout_link = self.driver.find_element(By.LINK_TEXT, "Logout")
            logout_link.click()
            self.wait.until(EC.url_contains("/login"))
        except:
            # If logout fails, just go to login page
            self.driver.get(f"{self.live_server_url}/login")

    def create_test_user(self, username="testuser", password=COMPLEX_PASSWORD, is_staff=False):
        """Helper method to create test user"""
        user = User.objects.create_user(
            username=username,
            password=password,
            email=f"{username}@example.com"
        )
        if is_staff:
            user.is_staff = True
            user.save()
        return user