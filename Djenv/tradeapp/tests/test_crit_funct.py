import pytest
from selenium.webdriver.common.by import By
from django.contrib.auth.models import User
from tradeapp.models import Offer
import time

class TestAuthentication:
    """Тесты для критических функций аутентификации"""
    
    def test_successful_login(self, login_page, test_user):
        """Тест успешного входа в систему"""
        original_url = login_page.get_current_url()
        login_page.login('testuser', 'testpassword123')
        
        login_page.wait_for_url_change(original_url)
        assert login_page.is_login_successful()
    
class TestOfferManagement:
    """Тесты для управления предложениями"""
    
    def test_create_offer(self, create_offer_page, test_user):
        """Тест создания нового предложения"""
        create_offer_page.create_offer(
            title="Test Offer Selenium",
            description="This is a test offer description from Selenium",
            price=99.99
        )
        time.sleep(3)
        assert create_offer_page.is_offer_created_successfully()
    
    def test_create_offer_with_negative_price(self, create_offer_page):
        """Тест валидации отрицательной цены"""
        create_offer_page.create_offer(
            title="Invalid Price Offer",
            description="Test with negative price",
            price=-10.00
        )
        time.sleep(2)

        error_message = create_offer_page.get_error_message()
        if error_message:
            assert "price" in error_message.lower() or "negative" in error_message.lower()
        else:
            assert "create" in create_offer_page.get_current_url().lower()

class TestForumFunctionality:
    """Тесты для функциональности форума"""
    
    def test_forum_access_and_thread_creation(self, forum_page, test_user):
        """Тест доступа к форуму"""
        assert forum_page.is_forum_loaded()
        threads_count = forum_page.get_threads_count()
        assert threads_count >= 0 

        if test_user.is_staff:
            can_create = forum_page.create_thread("Test Thread")
            assert can_create

@pytest.mark.django_db
class TestUserRegistration:
    """Тесты регистрации пользователя"""
    
    def test_user_registration_flow(self, chrome_driver, live_server):
        """Тест доступа к странице регистрации"""
        chrome_driver.get(f"{live_server.url}/register")
        assert "register" in chrome_driver.current_url.lower()
        forms = chrome_driver.find_elements(By.TAG_NAME, "form")
        assert len(forms) > 0

@pytest.mark.staff
class TestAdminFunctionality:
    """Тесты для административных функций"""
    
    def test_offer_review_access(self, login_page, admin_user, live_server):
        """Тест доступа администратора к модерации офферов"""
        login_page.login('admin', 'adminpassword123')
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(login_page.driver, 10).until(
            EC.url_contains('home')
        )
        login_page.driver.get(f"{live_server.url}/review-offers")

        assert "review" in login_page.get_current_url().lower()
        assert login_page.is_element_present((By.TAG_NAME, "body"))

class TestSimpleAuthentication:
    """Упрощенные тесты аутентификации"""
    
    def test_failed_login_simple(self, login_page):
        """Упрощенный тест неудачного логина"""
        original_url = login_page.get_current_url()

        login_page.login('wronguser', 'wrongpassword')
        time.sleep(3)

        current_url = login_page.get_current_url()
        assert "login" in current_url.lower() or original_url == current_url, \
            f"Expected to remain on login page, but got: {current_url}"