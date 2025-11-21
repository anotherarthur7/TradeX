import pytest
from selenium.webdriver.common.by import By

class TestNavigation:
    """Тесты навигации по сайту"""
    
    def test_sidebar_navigation(self, logged_in_home_page):
        """Тест что sidebar правильно отображается"""
        # Проверяем наличие основных ссылок в sidebar
        assert logged_in_home_page.is_element_present(logged_in_home_page.CREATE_OFFER_LINK)
        assert logged_in_home_page.is_element_present(logged_in_home_page.FORUM_LINK)
        assert logged_in_home_page.is_element_present(logged_in_home_page.OFFERS_LINK)
        assert logged_in_home_page.is_element_present(logged_in_home_page.PROFILE_LINK)
    
    def test_navigate_to_create_offer(self, logged_in_home_page):
        """Тест перехода к созданию оффера через sidebar"""
        logged_in_home_page.navigate_to_create_offer()
        
        # Проверяем что перешли на страницу создания
        assert "create" in logged_in_home_page.get_current_url().lower()
    
    def test_navigate_to_forum(self, logged_in_home_page):
        """Тест перехода к форуму через sidebar"""
        logged_in_home_page.navigate_to_forum()
        
        # Проверяем что перешли на форум
        assert "forum" in logged_in_home_page.get_current_url().lower()