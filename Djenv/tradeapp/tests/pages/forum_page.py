from selenium.webdriver.common.by import By
from .base_page import BasePage

class ForumPage(BasePage):
    # Локаторы основаны на forum/thread_list.html
    THREAD_LIST = (By.CLASS_NAME, "thread-list")
    CREATE_THREAD_BUTTON = (By.LINK_TEXT, "Create New Thread")
    THREAD_ITEMS = (By.CLASS_NAME, "thread-item")
    
    def is_forum_loaded(self):
        return self.is_element_present(self.THREAD_LIST)
    
    def create_thread(self, topic):
        if self.is_element_present(self.CREATE_THREAD_BUTTON):
            create_btn = self.find_clickable_element(self.CREATE_THREAD_BUTTON)
            create_btn.click()
            
            # Здесь будет логика для формы создания темы
            # Пока просто возвращаем True если кнопка найдена
            return True
        return False
    
    def get_threads_count(self):
        return len(self.driver.find_elements(*self.THREAD_ITEMS))