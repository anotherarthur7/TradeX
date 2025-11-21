import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
from tradeapp.models import Profile, Offer
import django
import os
from django.conf import settings

# Настройка Django перед импортом моделей
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djenv.settings')
    django.setup()

@pytest.fixture(scope='function')
def chrome_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpassword123'
    )
    Profile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def admin_user(db):
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword123'
    )
    Profile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def login_page(chrome_driver, live_server):
    chrome_driver.get(f"{live_server.url}/login")
    from tradeapp.tests.pages.login_page import LoginPage
    return LoginPage(chrome_driver)

@pytest.fixture
def logged_in_home_page(login_page, test_user):
    """Фикстура для уже залогиненного пользователя"""
    login_page.login('testuser', 'testpassword123')
    
    # Ждем редирект
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    WebDriverWait(login_page.driver, 10).until(
        EC.url_contains('home')
    )
    
    from tradeapp.tests.pages.home_page import HomePage
    return HomePage(login_page.driver)

@pytest.fixture
def create_offer_page(logged_in_home_page, live_server):
    """Фикстура для страницы создания оффера"""
    logged_in_home_page.driver.get(f"{live_server.url}/create")
    from tradeapp.tests.pages.offer_page import OfferPage
    return OfferPage(logged_in_home_page.driver)

@pytest.fixture
def forum_page(logged_in_home_page, live_server):
    """Фикстура для страницы форума"""
    logged_in_home_page.driver.get(f"{live_server.url}/forum")
    from tradeapp.tests.pages.forum_page import ForumPage
    return ForumPage(logged_in_home_page.driver)