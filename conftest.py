from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pytest


@pytest.fixture()
def driver():

    options = webdriver.ChromeOptions()  # дополнительные настройки для браузера
    options.add_experimental_option('detach', True)  # опция, которая не позволит Chrome закрыться
    options.add_argument("--guest")  # опция, которая отключает оповещения с просьбой смены пароля
    options.add_argument('--disable-translate')  # отключаем предложение перевести страницу
    options.add_argument('--disable-features=Translate')
    service = ChromeService(ChromeDriverManager().install())
    try:
        driver_ = webdriver.Chrome(service=service, options=options)
        driver_.implicitly_wait(3)
        yield driver_
        driver_.close()

    except Exception as e:
        print(f'Ошибка при запуске браузера:\n{e}')


