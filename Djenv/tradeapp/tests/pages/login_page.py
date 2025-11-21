from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    # Локаторы основаны на вашем реальном HTML
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    REMEMBER_ME_CHECKBOX = (By.ID, "remember_me")
    LOGIN_BUTTON = (By.XPATH, "//button[@type='submit']")
    ERROR_MESSAGE = (By.ID, "error-message")
    
    def enter_username(self, username):
        username_field = self.find_element(self.USERNAME_INPUT)
        username_field.clear()
        username_field.send_keys(username)
    
    def enter_password(self, password):
        password_field = self.find_element(self.PASSWORD_INPUT)
        password_field.clear()
        password_field.send_keys(password)
    
    def set_remember_me(self, remember):
        checkbox = self.find_element(self.REMEMBER_ME_CHECKBOX)
        if remember and not checkbox.is_selected():
            checkbox.click()
        elif not remember and checkbox.is_selected():
            checkbox.click()
    
    def click_login(self):
        login_btn = self.find_clickable_element(self.LOGIN_BUTTON)
        login_btn.click()
    
    def login(self, username, password, remember_me=False):
        self.enter_username(username)
        self.enter_password(password)
        self.set_remember_me(remember_me)
        self.click_login()
    
    def get_error_message(self):
        if self.is_element_present(self.ERROR_MESSAGE):
            element = self.find_element(self.ERROR_MESSAGE)
            return element.text if element.is_displayed() else None
        return None
    
    def is_login_successful(self):
        # Проверяем редирект на домашнюю страницу
        return "home" in self.get_current_url().lower()