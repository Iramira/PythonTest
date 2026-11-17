"""
Тесты сайта service-online.su (генератор ценников) в браузере Google Chrome.

Используется Chrome.
Логин и пароль не хранятся в коде: они берутся из файла .env, который не загружается на GitHub.
PDF сохраняется во временную папку, которая удаляется после теста,поэтому тесты не зависят от папки «Загрузки» и от прошлых запусков.
Вместо фиксированных time.sleep() ждёт нужные элементы и файл (WebDriverWait), поэтому тесты быстрее и стабильнее.

"""

import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path

from dotenv import load_dotenv
from pdfminer.high_level import extract_text
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Загружаем переменные из .env, который лежит рядом с этим файлом.
# Так тест работает независимо от того, из какой папки его запустили.
load_dotenv(Path(__file__).with_name(".env"))

URL = "https://service-online.su/forms/cenniki/"
LOGIN = os.getenv("SERVICE_ONLINE_LOGIN")
PASSWORD = os.getenv("SERVICE_ONLINE_PASSWORD")
# Для входа сайт требует две галочки: согласие на обработку персональных данных и принятие пользовательского соглашения.
# Автотест не соглашается на юридические условия молча, поэтому галочки ставятся, только если в .env будет явно указано SERVICE_ONLINE_ACCEPT_TERMS=1.
ACCEPT_TERMS = os.getenv("SERVICE_ONLINE_ACCEPT_TERMS") == "1"

# Максимальное время ожидания элементов страницы и скачивания файла, сек.
TIMEOUT = 15
DOWNLOAD_TIMEOUT = 30
# Папка для снимков экрана и HTML страницы при сбое.
DEBUG_DIR = Path(__file__).with_name("debug")
# Валюта из выпадающего списка.
CURRENCY = "₽ российский рубль"


def wait_for_pdf(folder: Path, timeout: int = DOWNLOAD_TIMEOUT) -> Path:
    """Ждёт, пока в папке появится полностью скачанный PDF, и возвращает путь.

    Пока Chrome качает файл, у него расширение .crdownload,
    поэтому ищем только готовые *.pdf.
    """
    end_time = time.monotonic() + timeout
    while time.monotonic() < end_time:
        pdf_files = list(folder.glob("*.pdf"))
        in_progress = list(folder.glob("*.crdownload"))
        if pdf_files and not in_progress:
            return pdf_files[0]
        time.sleep(0.5)
    raise AssertionError(
        f"За {timeout} с PDF-файл не появился в папке {folder}")


@unittest.skipUnless(
    LOGIN and PASSWORD,
    "Не заданы SERVICE_ONLINE_LOGIN и SERVICE_ONLINE_PASSWORD (см. .env.example)",
)
class PriceChromeTestCase(unittest.TestCase):
    """Авторизация и скачивание ценников в формате PDF."""

    def setUp(self):
        self.download_dir = Path(tempfile.mkdtemp(prefix="cenniki_"))
        self.addCleanup(shutil.rmtree, self.download_dir, ignore_errors=True)

        options = Options()
        options.add_argument("--log-level=3")
        options.add_experimental_option("prefs", {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
        })

        # options.add_argument("--headless=new") - раскомментировать в случае запуска без окна браузера

        self.driver = webdriver.Chrome(options=options)
        self.addCleanup(self.driver.quit)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, TIMEOUT)

        self.driver.get(URL)
        self.login()

    def tearDown(self):
        try:
            menu = self.driver.find_element(By.ID, "menu")
            menu.find_elements(By.TAG_NAME, "li")[-1].click()
        except Exception as error:
            print(f"Не удалось выйти с сайта: {error}")

    # вспомогательные методы

    def save_debug(self, reason: str) -> Path:
        """Сохраняет снимок экрана и HTML страницы, чтобы разобрать сбой."""
        DEBUG_DIR.mkdir(exist_ok=True)
        name = f"{self._testMethodName}_{reason}"
        screenshot = DEBUG_DIR / f"{name}.png"
        self.driver.save_screenshot(str(screenshot))
        (DEBUG_DIR / f"{name}.html").write_text(
            self.driver.page_source, encoding="utf-8"
        )
        return screenshot

    def safe_click(self, element):
        """Обычный клик, а если элемент перекрыт или скрыт стилями — клик через JS.

        Так бывает с «красивыми» чекбоксами, у которых сам input невидим.
        """
        try:
            element.click()
        except (ElementClickInterceptedException, ElementNotInteractableException):
            self.driver.execute_script("arguments[0].click();", element)

    def find_first_visible(self, locators):
        """Ждёт первый видимый элемент из нескольких вариантов локаторов."""
        def search(driver):
            for by, value in locators:
                for element in driver.find_elements(by, value):
                    if element.is_displayed():
                        return element
            return False

        return self.wait.until(search)

    def accept_cookies(self):
        """Закрывает плашку о cookie, если она есть: она перекрывает
        галочку согласия и кнопку «Войти» в окне авторизации."""
        for element in self.driver.find_elements(
            By.XPATH, "//*[normalize-space(text())='Понятно']"
        ):
            if element.is_displayed():
                self.safe_click(element)
                return

    def login(self):
        """Открывает окно входа, вводит логин и пароль, закрывает окно."""
        self.wait.until(
            lambda d: d.execute_script(
                "return document.readyState") == "complete"
        )
        self.accept_cookies()
        self.safe_click(
            self.wait.until(EC.element_to_be_clickable((By.ID, "enter")))
        )

        # Форма входа на сайте загружается во встроенном фрейме (iframe со страницей /auth/login.php).
        # Selenium не видит элементы внутри фрейма,пока в него не переключится.
        try:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe.featherlight-inner")
            ))
            login_field = self.find_first_visible([
                (By.NAME, "login"),
                (By.CSS_SELECTOR, "input[type=email]"),
                (By.CSS_SELECTOR, "input[placeholder=Email]"),
            ])
        except TimeoutException:
            screenshot = self.save_debug("login_form")
            # Если сайт ограничил частоту запросов (HTTP 429), это не ошибка, в тесте: пропускаем его с понятным сообщением.
            if "429 Too Many Requests" in self.driver.page_source:
                self.driver.switch_to.default_content()
                self.skipTest(
                    "Сайт временно ограничил число запросов (429 Too Many "
                    "Requests). Подождите 15–30 минут и запустите тесты снова."
                )
            raise AssertionError(
                "Окно авторизации не открылось или поле Email не найдено. "
                f"Снимок экрана: {screenshot}"
            ) from None

        self.accept_cookies()

        # Проверка согласий ДО ввода логина и пароля: без разрешения пользователя данные на сайт не отправляются.
        consent_boxes = [
            box for name in ("soglasie", "soglasie2")
            for box in self.driver.find_elements(By.NAME, name)
        ]
        if consent_boxes and not ACCEPT_TERMS:
            self.driver.switch_to.default_content()
            self.skipTest(
                "Для входа сайт требует согласие на обработку персональных "
                "данных и принятие пользовательского соглашения. Чтобы тест "
                "ставил галочки, добавьте в .env SERVICE_ONLINE_ACCEPT_TERMS=1"
            )

        login_field.send_keys(LOGIN)
        self.find_first_visible([
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type=password]"),
        ]).send_keys(PASSWORD)

        for box in consent_boxes:
            if not box.is_selected():
                self.safe_click(box)

        self.safe_click(self.find_first_visible([
            (By.NAME, "test_enter"),
            (By.CSS_SELECTOR, "[type=submit]"),
        ]))

        try:
            self.wait.until(EC.staleness_of(login_field))
        except TimeoutException:
            screenshot = self.save_debug("login_submit")
            raise AssertionError(
                "Форма входа не отправилась (неверный логин/пароль, "
                f"не все галочки согласия, капча или блокировка). Снимок экрана: {screenshot}"
            ) from None
        finally:
            self.driver.switch_to.default_content()

        for button in self.driver.find_elements(
            By.CSS_SELECTOR, "button[aria-label=Close]"
        ):
            if button.is_displayed():
                self.safe_click(button)
        self.wait.until(lambda d: not any(
            b.is_displayed()
            for b in d.find_elements(By.CSS_SELECTOR, "button[aria-label=Close]")
        ))

    def fill_price_form(self, company, date, unit, country, product, price):
        """Заполняет форму одного ценника."""
        field = self.wait.until(
            EC.visibility_of_element_located((By.ID, "comp_name"))
        )
        field.clear()
        field.send_keys(company)

        field = self.driver.find_element(By.ID, "date")
        field.clear()
        field.send_keys(date)

        Select(
            self.driver.find_element(By.NAME, "currency_code")
        ).select_by_visible_text(CURRENCY)

        self.driver.find_element(By.ID, "tovar_ed_default").send_keys(unit)
        self.driver.find_element(
            By.ID, "tovar_country_default").send_keys(country)

        # Первая строка таблицы товаров.
        row = self.driver.find_element(By.CSS_SELECTOR, "#tab1 tbody tr")
        row.find_element(
            By.CSS_SELECTOR, ".tovar_name textarea").send_keys(product)
        row.find_element(By.CSS_SELECTOR, ".tovar_cena input").send_keys(price)

    def download_pdf_text(self) -> str:
        """Нажимает «Скачать», ждёт PDF и возвращает его текст."""
        self.wait.until(EC.element_to_be_clickable(
            (By.ID, "download"))).click()
        pdf_path = wait_for_pdf(self.download_dir)
        return extract_text(str(pdf_path))

    # тесты

    def test_authorization(self):
        """После входа в меню есть ссылка «Личный кабинет»."""

        try:
            self.wait.until(EC.text_to_be_present_in_element(
                (By.ID, "menu"), "Личный"
            ))
        except TimeoutException:
            self.save_debug("menu")
        menu = self.driver.find_element(By.ID, "menu")
        self.assertIn("Личный\nкабинет", menu.text)

    def test_one_price_en(self):
        """Ценник на английском: введённые данные есть в PDF."""
        self.fill_price_form(
            company="Eurotorg",
            date="2025/08/20",
            unit="kg",
            country="RU",
            product="Candy Southern Night",
            price="10.55",
        )
        text = self.download_pdf_text()

        for expected in ("Eurotorg", "2025/08/20", "kg", "RU",
                         "Candy Southern Night"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_one_price_ru(self):
        """Ценник на русском: введённые данные есть в PDF."""
        self.fill_price_form(
            company="ООО Евроторг",
            date="20.08.2025",
            unit="кг",
            country="РФ",
            product="Конфеты Южная ночь",
            price="10,55",
        )
        text = self.download_pdf_text()

        for expected in ("ООО Евроторг", "20.08.2025", "кг", "РФ",
                         "Конфеты Южная ночь", "10", "55"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
