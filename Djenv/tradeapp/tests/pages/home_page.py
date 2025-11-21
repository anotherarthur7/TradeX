from selenium.webdriver.common.by import By
from .base_page import BasePage

class HomePage(BasePage):
    # Локаторы основаны на вашей sidebar из base.html
    CREATE_OFFER_LINK = (By.ID, "create-offer-link")
    FORUM_LINK = (By.XPATH, "//a[contains(@href, '/forum')]")
    OFFERS_LINK = (By.XPATH, "//a[contains(@href, '/offermain')]")
    PROFILE_LINK = (By.XPATH, "//a[contains(@href, '/profile')]")
    LOGOUT_LINK = (By.XPATH, "//a[contains(@href, '/logout')]")
    
    def navigate_to_create_offer(self):
        create_link = self.find_clickable_element(self.CREATE_OFFER_LINK)
        create_link.click()
    
    def navigate_to_forum(self):
        forum_link = self.find_clickable_element(self.FORUM_LINK)
        forum_link.click()
    
    def navigate_to_offers(self):
        offers_link = self.find_clickable_element(self.OFFERS_LINK)
        offers_link.click()
    
    def navigate_to_profile(self):
        profile_link = self.find_clickable_element(self.PROFILE_LINK)
        profile_link.click()
    
    def click_logout(self):
        logout_link = self.find_clickable_element(self.LOGOUT_LINK)
        logout_link.click()