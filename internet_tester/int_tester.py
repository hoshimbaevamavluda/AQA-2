import os

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, sync_playwright, expect

load_dotenv()

BASE_URL = "https://the-internet.herokuapp.com/"
TITLE = "the-internet"
TITLE_FORM_AUTH = "Form Authentication"
TITLE_DROPDOWN = "Dropdown"

PAGE_LOGIN = "/login"


@pytest.fixture
def page():
    with sync_playwright() as drv:
        browser = drv.chromium.launch(headless=False)
        # print("Начало работы браузера")
        page_ = browser.new_page()
        page_.set_default_timeout(7000)
        page_.goto(BASE_URL)
        yield page_
        browser.close()
        # print("Завершение работы браузера")


def navigate_to_example(page, example_name: str):
    el_form_auth = page.get_by_role("link", name=example_name)
    el_form_auth.click()
    return page.url


def assert_text_in_url_print(page, text_expected: str, msg: str = ""):
    assert text_expected in page.url, "Не та страница!"
    print(f"\n{msg}URL: {page.url}")


def assert_subtext_in_text(subtext: str, text: str, msg: str = ""):
    assert subtext in text, \
        f"{msg}'{text}' не содержит '{subtext}'"


def test_01(page):
    """ 🌐26x01: Базовый вход на сайт """
    # print("-- Начало Тест-кейс 1")
    page.wait_for_timeout(200)

    el_head = page.get_by_role("heading", name="to the-internet")
    el_head_text = el_head.inner_text()
    assert_subtext_in_text(TITLE,  el_head_text, "Заголовок ")


def test_02(page):
    """ 🌐26x02: Навигация по ссылкам """
    navigate_to_example(page, TITLE_FORM_AUTH)
    assert_text_in_url_print(page, PAGE_LOGIN,
                             "✅ Перешли в: Form Authentication | ")


def test_03(page):
    """ 🌐26x03: Форма логина (Fill + Click) """
    navigate_to_example(page, TITLE_FORM_AUTH)
    field_username = page.locator("#username")
    field_password = page.locator("#password")
    env_username = os.environ.get("USER")
    env_password = os.environ.get("PASS")
    field_username.fill(env_username)
    field_password.fill(env_password)
    btn_login = page.get_by_role("button", name="Login")
    btn_login.click()
    assert_text_in_url_print(page, "/secure",
                             "✅ Успешный вход! ")


def test_04(page):
    """
    🌐26x04: Выход из системы (Logout)

    :param: page - фикстура браузер + страница
    :return: None
    """
    test_03(page)
    btn_logout = page.get_by_role("link", name="Logout")
    btn_logout.click()
    assert_text_in_url_print(page, PAGE_LOGIN,
                             "✅ Успешный выход! ")

def test_05(page):
    """ 🌐26x05 """
    navigate_to_example(page, "Checkboxes")
    chkbox1 = page.locator("#checkboxes input:nth-child(1)")
    chkbox2 = page.locator("#checkboxes input:nth-child(3)")
    print(f"{chkbox1.is_visible()=}")
    print(f"{chkbox1.is_enabled()=}")
    print(f"{chkbox1.is_checked()=}")
    print(f"{chkbox2.is_checked()=}")

    chkbox1.check()
    chkbox2.uncheck()

    print(f"✅ Checkbox 1: checked={chkbox1.is_checked()}")
    print(f"✅ Checkbox 2: checked={chkbox2.is_checked()}")


def test_06(page):
    navigate_to_example(page, TITLE_DROPDOWN)
    dropdown = page.locator("#dropdown")
    select_1 = page.locator("#dropdown option:nth-child(1)")
    select_1_text = select_1.inner_text()
    assert_subtext_in_text("Please select an option",  select_1_text, "Элемент ")
    dropdown.click()

def test_07(page):
    navigate_to_example(page,"Inputs")
    loc_numb = "//input[@type='number']"
    page.fill(loc_numb, "123")
    txt_number = page.locator(loc_numb).input_value()
    print(txt_number)
    page.locator(loc_numb).fill("456")
    print("✅ Введено: 456")

def test_08(page):
    navigate_to_example(page, "Hovers")
    page.hover("div:nth-child(3) > img")
    user1 = page.locator("div:nth-child(3) > div > h5")
    txt_user1 = user1.inner_text()
    assert_subtext_in_text("name: user1", txt_user1)
