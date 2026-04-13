import os
from asyncio import wait_for

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
    page.goto(BASE_URL)
    page.get_by_role("link", name=example_name).click()
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
    page.get_by_role("textbox", name="Username").fill("tomsmith")
    page.get_by_role("textbox", name="Password").fill("SuperSecretPassword!")

    page.get_by_role("button", name="Login").click()

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
    page.fill(loc_numb, input())
    txt_number = page.locator(loc_numb).input_value()
    print(txt_number)
    page.locator(loc_numb).fill(input())
    print(f"✅ Введено: {us_input}")


def test_08(page):
    navigate_to_example(page, "Hovers")
    page.hover("div:nth-child(3) > img")
    user1 = page.locator("div:nth-child(3) > div > h5")
    txt_user1 = user1.inner_text()
    assert_subtext_in_text("name: user1", txt_user1)


def test_09(page):
    navigate_to_example(page, "JavaScript Alerts")
    page.on("dialog", lambda dialog: dialog.accept())
    btn_alert = page.get_by_role("button", name="Click for JS Alert")
    btn_alert.click()
    result = page.locator("#result")
    txt_result = result.inner_text()
    assert_subtext_in_text("You successfully clicked an alert", txt_result)
    print(f"✅ Alert принят. Сообщение: {txt_result}")


def test_10(page):
    with open("test_upload.txt", "w") as file:
        file.write("Hello Playwright")

    navigate_to_example(page, "File Upload")

    page.set_input_files("#file-upload", "test_upload.txt")

    page.click("#file-submit")

    expect(page.locator("#uploaded-files")).to_have_text("test_upload.txt")
    print(f"✅ Файл загружен: test_upload.txt")


def test_11(page):
    navigate_to_example(page, "Dynamic Loading")
    exampl_1 = page.locator("a:nth-child(5)")
    exampl_1.click()
    btn_start = page.get_by_role("button", name="Start")
    btn_start.click()
    page.wait_for_selector("#finish")
    expect(page.locator("#finish")).to_have_text("Hello World!")
    print("✅ Элемент появился: Hello World!")


def run_full_test(page):
    results = {}

    # 1. Form Authentication (вход + выход)
    try:
        navigate_to_example(page, "Form Authentication")

        page.get_by_role("textbox", name="Username").fill("tomsmith")
        page.get_by_role("textbox", name="Password").fill("SuperSecretPassword!")

        page.get_by_role("button", name="Login").click()

        assert "/secure" in page.url, "Не удалось войти"

        page.screenshot(path="form_auth_login_success.png")

        page.get_by_role("link", name="Logout").click()
        assert "/login" in page.url, "Не удалось выйти"

        page.screenshot(path="form_auth_logout_success.png")
        results["Form Authentication"] = True

    except Exception as e:
        print(f"Ошибка в Form Authentication: {e}")
        results["Form Authentication"] = False


    # 2. Checkboxes
    try:
        navigate_to_example(page, "Checkboxes")

        chkbox1 = page.locator("#checkboxes input").nth(0)
        chkbox2 = page.locator("#checkboxes input").nth(1)

        chkbox1.check()
        chkbox2.uncheck()

        assert chkbox1.is_checked(), "Checkbox 1 не отмечен"
        assert not chkbox2.is_checked(), "Checkbox 2 не снят"

        page.screenshot(path="checkboxes_success.png")
        results["Checkboxes"] = True

    except Exception as e:
        print(f"Ошибка в Checkboxes: {e}")
        results["Checkboxes"] = False

    # 3. Dropdown
    try:
        navigate_to_example(page, "Dropdown")

        dropdown = page.locator("#dropdown")
        dropdown.select_option("2")

        selected_value = dropdown.input_value()
        assert selected_value == "2", "Option 2 не выбрана"

        page.screenshot(path="dropdown_success.png")
        results["Dropdown"] = True

    except Exception as e:
        print(f"Ошибка в Dropdown: {e}")
        results["Dropdown"] = False

    # 4. Inputs
    try:
        navigate_to_example(page, "Inputs")

        input_field = page.locator("input[type='number']")
        input_field.fill("999")

        assert input_field.input_value() == "999", "Число 999 не введено"

        page.screenshot(path="inputs_success.png")
        results["Inputs"] = True

    except Exception as e:
        print(f"Ошибка в Inputs: {e}")
        results["Inputs"] = False

    # 5. Hovers
    try:
        navigate_to_example(page, "Hovers")

        first_image = page.locator(".figure").nth(0)
        first_image.hover()

        user_text = page.locator(".figure").nth(0).locator("h5").inner_text()
        assert "name: user1" in user_text, "Не появился текст user1"

        page.screenshot(path="hovers_success.png")
        results["Hovers"] = True

    except Exception as e:
        print(f"Ошибка в Hovers: {e}")
        results["Hovers"] = False

    # Отчёт
    print("\n📊 ОТЧЁТ:")
    for section, status in results.items():
        print(f"{'✅' if status else '❌'} {section}")

    if all(results.values()):
        print("\nВсе тесты пройдены!")
    else:
        print("\nЕсть ошибки в некоторых разделах.")

    return results


def test_12(page):
    run_full_test(page)
