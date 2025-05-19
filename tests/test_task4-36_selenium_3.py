from random import randint
import time
from constants.ansi import *
# импорт модулей отдельных страниц проекта
from pages.home import HomePage
from pages.inventory import Inventory_Page
from pages.cart import Cart_Page
from pages.checkout_step_one import Checkout_step_one_Page
from pages.checkout_step_two import Checkout_step_two_Page
from pages.checkout_complete import Checkout_complete_Page
from checking.checking import Checking

# собираем URL страниц из модулей отдельных страниц
home_url = HomePage.page_url
inventory_url = Inventory_Page.page_url
cart_url = Cart_Page.page_url
checkout_step_one_url = Checkout_step_one_Page.page_url
checkout_step_two_url = Checkout_step_two_Page.page_url
checkout_complete_url = Checkout_complete_Page.page_url


def get_random_numbers(count, maxnum):
    """ возвращаем count случайных неповторяющихся целых чисел между 0 и maxnum
        применение: выбрать X разных элементов какого-то списка
    """
    random_numbers_list = list()
    if count < 0 or count > maxnum or maxnum < 0:
        return random_numbers_list

    while len(random_numbers_list) < count:
        random_num = randint(0, maxnum)
        if random_num not in random_numbers_list:
            random_numbers_list.append(random_num)

    return random_numbers_list


def select_products():
    products_available_list = [
        {"name": "Sauce Labs Backpack", "price": "$29.99"},
        {"name": "Sauce Labs Bike Light", "price": "$9.99"},
        {"name": "Sauce Labs Bolt T-Shirt", "price": "$15.99"},
        {"name": "Sauce Labs Fleece Jacket", "price": "$49.99"},
        {"name": "Sauce Labs Onesie", "price": "$7.99"},
        {"name": "Test.allTheThings() T-Shirt (Red)", "price": "$15.99"}]

    welcome_msg = f'{WHITE}Вас приветствует система тестирования магазина www.saucedemo.com{RESET}'
    asteri = '*' * len(welcome_msg)
    print(f'{asteri}\n{welcome_msg}\n{asteri}')
    print(f'\n{SKY_BLUE}Чтобы начать тестирование, пожалуйста выберите один или несколько товаров из списка (0 - выход)'
          f':{RESET}\n')

    for index, product in enumerate(products_available_list, start=1):
        print(f'Товар {WHITE}# {index}{RESET}: {SKY_BLUE}{product["name"]}{RESET}, '
              f'цена {GREEN}{product["price"]}{RESET}')
    print()

    while True:
        try:
            selection = list(map(int, input('Введите номера товаров: ').split()))
            # если на вход подан 0, выходим из программы
            if selection == [0]:
                return []
            if len(selection) > len(products_available_list):
                print(f'{YELLOW}Вы указали слишком много номеров, должно быть не больше '
                      f'{len(products_available_list)}{RESET}.')
                continue
            # проверка, что все номера в допустимом диапазоне
            if all(1 <= number <= len(products_available_list) for number in selection):
                # print(f'{GREEN}Вы выбрали: {selection}{RESET}')
                user_selected_products = []
                for number in list(set(selection)):  # забираем номера из списка, очищенного от дубликатов
                    name = products_available_list[number-1]['name']
                    price = float(products_available_list[number-1]['price'].replace('$',''))
                    price = round(price, 2)  # решаем проблему, когда вылазит 0.0000001 в значениях
                    user_selected_products.append({
                            'name': name,
                            'price': price
                    })
                print(f'\n{WHITE}Итого, вы выбрали следующие товары для теста:{RESET}')
                summ = 0
                for product in user_selected_products:
                    summ += product['price']
                    summ = round(summ, 2)  # решаем проблему, когда вылазит 0.0000001 в значениях
                    print(f'- {SKY_BLUE}{product["name"]}{RESET}, цена {GREEN}{product["price"]}{RESET}')
                print(f'{WHITE}На общую сумму: {GREEN}$ {summ}{RESET}\n')
                return user_selected_products, summ  # возвращаем список объектов товаров и подсчитанную сумму
            else:
                raise ValueError
        except ValueError:
            print(f'{YELLOW}Некорректный выбор, укажите числа от 1 до {len(products_available_list)}, '
                  f'разделенные пробелами (0 - выход).{RESET}')




def test_smoke(driver):
    """ основной код смоук-текст сайта
        driver - функция-фикстура из conftest.py """

    STEP_PAUSE = 1

    # получаем список объектов товаров для тестов из консоли, где:
    #   user_selection = [товар1, товар2, товар N]
    #   товар N = {
    #               'name': имя товара,
    #               'price': цена товара (float)
    #             }
    #   user_selection_summ = стоимость выбранного в консоли

    user_selection, user_selection_summ = select_products()
    if len(user_selection) == 0:  # выход из теста по команде пользователя
        return

    # сохраняем множество из имен товаров для будущего сравнения с товарами со страницы
    selected_names = {product["name"] for product in user_selection}


    homepage = HomePage(driver)
    inventory_page = Inventory_Page(driver)
    cart_page = Cart_Page(driver)
    checkout_step_one_page = Checkout_step_one_Page(driver)
    checkout_step_two_page = Checkout_step_two_Page(driver)
    checkout_complete_page = Checkout_complete_Page(driver)

    homepage.open()
    Checking.check_url_change(driver, initial_url=home_url, expected_url=home_url, timeout=0)
    time.sleep(STEP_PAUSE)

    homepage.click_login()
    homepage.check_login_error()
    time.sleep(STEP_PAUSE)

    Checking.check_url_change(driver, initial_url=home_url, expected_url=inventory_url, timeout=1)

    products_list = inventory_page.get_products()  # получаем список товаров со страницы магазина
    products_list_cart = list()  # создаем список товаров, добавляемых в корзину
    products_summ = 0  # сумма всех товаров, добавляемых в корзину

    print('Список товаров на странице:')
    for i, product in enumerate(products_list, start=0):
        product_msg = f"{WHITE}Товар #{i}: {SKY_BLUE}{product['name']}{RESET}, " \
                      f"цена {GREEN}{product['price']}{RESET}"
        print(product_msg)
        if product['name'] in selected_names:
            # товар найден, добавляем в корзину
            products_list_cart.append(product)  # с этим списком потом будем сверять страницу корзины
            product_add_to_card_button_id = product['add_to_card_button_id']
            product_price = float(product['price'].replace('$', ''))
            product_price = round(product_price, 2)  # избавляемся от артефактов float 0.0000001
            products_summ += product_price
            products_summ = round(products_summ, 2)  # избавляемся от артефактов float 0.0000001
            # клик на кнопке "Add to card" для каждого товара
            inventory_page.add_to_card(product_add_to_card_button_id)
            time.sleep(1)


    assert user_selection_summ == products_summ, "Ошибка: сумма товаров из консоли не совпадает с суммой товаров, " \
                                                 "добавленных в корзину"

    print(f' -- Добавление в корзину: В корзину отправлено {len(products_list_cart)} товаров на сумму ${products_summ}')

    inventory_page.click_cart()
    Checking.check_url_change(driver, initial_url=inventory_url, expected_url=cart_url, timeout=1)
    time.sleep(STEP_PAUSE)

    cart_products_list = cart_page.get_cart_products()
    Checking.compare_cart_with_selected_products(products_list_cart, cart_products_list)

    time.sleep(STEP_PAUSE)
    cart_page.click_checkout()
    Checking.check_url_change(driver, initial_url=cart_url, expected_url=checkout_step_one_url, timeout=1)

    first_name = 'John'
    last_name = 'Dow'
    zip_postal_code = '111222333'

    checkout_step_one_page.fill_user_information(first_name, last_name, zip_postal_code)

    time.sleep(STEP_PAUSE)
    checkout_step_one_page.click_continue()
    Checking.check_url_change(driver, initial_url=checkout_step_one_url, expected_url=checkout_step_two_url, timeout=1)

    checkout_product_list = checkout_step_two_page.get_checkout_products()
    Checking.compare_cart_with_selected_products(checkout_product_list, cart_products_list)
    checkout_price = checkout_step_two_page.get_checkout_price_notaxes()  # + 100 для проверки ассерта
    Checking.compare_summ_cart_with_summ_checkout(products_summ, checkout_price)

    time.sleep(STEP_PAUSE)
    checkout_step_two_page.click_finish()
    Checking.check_url_change(driver, initial_url=checkout_step_two_url, expected_url=checkout_complete_url, timeout=1)

    print(f'{GREEN}Smoke-тест для {HomePage.page_url} пройден!{RESET}')
