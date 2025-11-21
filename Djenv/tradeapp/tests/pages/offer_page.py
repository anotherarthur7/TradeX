from selenium.webdriver.common.by import By
from .base_page import BasePage

class OfferPage(BasePage):
    # Локаторы основаны на create.html
    TITLE_INPUT = (By.NAME, "title")
    DESCRIPTION_INPUT = (By.NAME, "description")
    PRICE_INPUT = (By.NAME, "price")
    IMAGE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")
    SUCCESS_INDICATOR = (By.XPATH, "//h1[contains(text(), 'Offer Submitted')]")  # SweetAlert заголовок
    
    def create_offer(self, title, description, price, image_path=None):
        # Ждем загрузки формы
        self.find_element(self.TITLE_INPUT)
        
        title_field = self.find_element(self.TITLE_INPUT)
        title_field.clear()
        title_field.send_keys(title)
        
        desc_field = self.find_element(self.DESCRIPTION_INPUT)
        desc_field.clear()
        desc_field.send_keys(description)
        
        price_field = self.find_element(self.PRICE_INPUT)
        price_field.clear()
        price_field.send_keys(str(price))
        
        if image_path:
            image_field = self.find_element(self.IMAGE_INPUT)
            image_field.send_keys(image_path)
        
        submit_btn = self.find_clickable_element(self.SUBMIT_BUTTON)
        submit_btn.click()
    
    def is_offer_created_successfully(self):
        # Проверяем появление SweetAlert или редирект
        import time
        time.sleep(2)  # Ждем появления SweetAlert
        
        # Проверяем различные индикаторы успеха
        success_indicators = [
            (By.XPATH, "//*[contains(text(), 'Offer Submitted')]"),
            (By.XPATH, "//*[contains(text(), 'pending')]"),
            (By.XPATH, "//*[contains(text(), 'success')]")
        ]
        
        for selector in success_indicators:
            if self.is_element_present(selector):
                return True
        
        # Или проверяем редирект на домашнюю страницу
        return "home" in self.get_current_url().lower()
    
    def get_error_message(self):
        # Ищем ошибки формы
        error_selectors = [
            (By.CLASS_NAME, "form-error"),
            (By.XPATH, "//*[contains(@class, 'error')]"),
            (By.XPATH, "//*[contains(text(), 'error')]")
        ]
        
        for selector in error_selectors:
            if self.is_element_present(selector):
                return self.find_element(selector).text
        return None