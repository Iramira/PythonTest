"""
Альтернативный вариант тестов сайта service-online.su в Google Chrome:
тест сам ставит галочки согласия и проходит сценарий до конца.

Отличия от test_site_chrome.py:
- галочки «согласие на обработку персональных данных» и «пользовательское
  соглашение» ставятся всегда (учебный аккаунт, решение принято осознанно);
- поля таблицы товаров обновлены под текущую версию сайта: единица
  измерения и страна вводятся в строке товара (tovar_ed[], tovar_country[]),
  отдельных полей tovar_ed_default и tovar_country_default больше нет;
- ценник формируется кнопкой «Печать» (id="print_blank"), кнопки
  id="download" на странице больше нет; PDF берётся из встроенного
  просмотрщика сайта (pdf.js) или из папки загрузок.

Используется Chrome вместо Firefox;
Логин и пароль не хранятся в коде: они берутся из файла .env, который не загружается на GitHub;
PDF сохраняется во временную папку, которая удаляется после теста,поэтому тесты не зависят от папки «Загрузки» и от прошлых запусков;
Вместо фиксированных time.sleep() ждёт нужные элементы и файл (WebDriverWait), поэтому тесты быстрее и стабильнее.

"""

import base64
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
# Имена чекбоксов согласия на сайте.
CONSENT_NAMES = ("soglasie", "soglasie2")

# Максимальное время ожидания элементов страницы и скачивания файла, сек.
TIMEOUT = 15
DOWNLOAD_TIMEOUT = 30
# Папка для снимков экрана и HTML страницы при сбое.
DEBUG_DIR = Path(__file__).with_name("debug")
# Валюта из выпадающего списка.
CURRENCY = "₽ российский рубль"


@unittest.skipUnless(
    LOGIN and PASSWORD,
    "Не заданы SERVICE_ONLINE_LOGIN и SERVICE_ONLINE_PASSWORD (см. .env.example)",
)
class PriceChromeFullTestCase(unittest.TestCase):
    """Авторизация и печать ценников в PDF (с галочками согласия)."""

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
        # Время на выполнение асинхронного JavaScript (получение PDF).
        self.driver.set_script_timeout(DOWNLOAD_TIMEOUT)
        self.main_window = self.driver.current_window_handle

        self.driver.get(URL)
        self.login()

    def tearDown(self):
        try:
            # «Печать» может открыть новую вкладку — возвращаемся в основную.
            self.driver.switch_to.window(self.main_window)
            self.driver.switch_to.default_content()
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
            # Если сайт ограничил частоту запросов (HTTP 429), это не ошибка
            # в тесте: пропускаем его с понятным сообщением.
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

        # Галочки согласия во фрейме входа (в этом варианте ставятся всегда).
        consent_boxes = [
            box for name in CONSENT_NAMES
            for box in self.driver.find_elements(By.NAME, name)
        ]

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

    def tick_consents(self):
        """Ставит галочки согласия на основной странице, если они там есть
        (сайт может требовать их и перед кнопкой «Печать»)."""
        for name in CONSENT_NAMES:
            for box in self.driver.find_elements(By.NAME, name):
                if not box.is_selected():
                    self.safe_click(box)

    def type_into(self, element, text):
        """Очищает поле и вводит текст."""
        element.clear()
        element.send_keys(text)

    def fill_price_form(self, company, date, unit, country, product, price):
        """Заполняет общие настройки и первую строку таблицы товаров."""
        self.type_into(
            self.wait.until(EC.visibility_of_element_located(
                (By.ID, "comp_name"))),
            company,
        )
        self.type_into(self.driver.find_element(By.ID, "date"), date)

        Select(
            self.driver.find_element(By.NAME, "currency_code")
        ).select_by_visible_text(CURRENCY)

        # Первая видимая строка таблицы товаров. На сайте могут быть демонстрационные строки («Капучино Гранде»), поэтому поля очищаем.
        name_field = self.find_first_visible(
            [(By.CSS_SELECTOR, "#tab1 tbody textarea[name='tovar_name[]']")]
        )
        row = name_field.find_element(By.XPATH, "./ancestor::tr[1]")
        self.type_into(name_field, product)
        self.type_into(row.find_element(By.NAME, "tovar_ed[]"), unit)
        self.type_into(row.find_element(By.NAME, "tovar_cena[]"), price)
        self.type_into(row.find_element(By.NAME, "tovar_country[]"), country)

    def pdf_from_viewer(self, depth=0):
        """Ищет встроенный просмотрщик PDF (pdf.js) в текущем документе и
        во вложенных фреймах и возвращает содержимое PDF в base64."""
        data = self.driver.execute_async_script("""
            const done = arguments[arguments.length - 1];
            const app = window.PDFViewerApplication;
            if (!app || !app.pdfDocument) { done(null); return; }
            app.pdfDocument.getData().then(bytes => {
                let s = "";
                for (let i = 0; i < bytes.length; i += 0x8000) {
                    s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
                }
                done(btoa(s));
            }).catch(() => done(null));
        """)
        if data or depth >= 2:
            return data
        for frame in self.driver.find_elements(By.TAG_NAME, "iframe"):
            try:
                self.driver.switch_to.frame(frame)
                data = self.pdf_from_viewer(depth + 1)
            except Exception:  # фрейм рекламы и т. п. — пропускаем
                data = None
            finally:
                self.driver.switch_to.parent_frame()
            if data:
                return data
        return None

    def print_pdf_text(self) -> str:
        """Нажимает «Печать», получает PDF и возвращает его текст."""
        windows_before = set(self.driver.window_handles)
        self.tick_consents()
        self.safe_click(self.find_first_visible([
            (By.ID, "print_blank"),
            (By.ID, "download"),
        ]))

        end_time = time.monotonic() + DOWNLOAD_TIMEOUT
        while time.monotonic() < end_time:
            # 1) Chrome сам скачал PDF в папку загрузок.
            pdf_files = list(self.download_dir.glob("*.pdf"))
            if pdf_files and not list(self.download_dir.glob("*.crdownload")):
                return extract_text(str(pdf_files[0]))

            # 2) PDF открылся в новой вкладке или во всплывающем окне сайта.
            new_windows = set(self.driver.window_handles) - windows_before
            for handle in [*new_windows, self.main_window]:
                self.driver.switch_to.window(handle)
                self.driver.switch_to.default_content()
                data = self.pdf_from_viewer()
                if data:
                    self.driver.switch_to.window(self.main_window)
                    pdf_path = self.download_dir / "cennik.pdf"
                    pdf_path.write_bytes(base64.b64decode(data))
                    return extract_text(str(pdf_path))

            # 3) Сайт показал сообщение (например, о галочках) — фиксируем.
            self.driver.switch_to.window(self.main_window)
            for dialog in self.driver.find_elements(By.CSS_SELECTOR, ".fd-body"):
                if dialog.is_displayed():
                    screenshot = self.save_debug("print_dialog")
                    raise AssertionError(
                        f"Сайт показал сообщение: {dialog.text!r}. "
                        f"Снимок экрана: {screenshot}"
                    )
            time.sleep(0.5)

        self.driver.switch_to.window(self.main_window)
        screenshot = self.save_debug("print_pdf")
        raise AssertionError(
            f"За {DOWNLOAD_TIMEOUT} с PDF не появился. Снимок экрана: {screenshot}"
        )

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
        text = self.print_pdf_text()

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
        text = self.print_pdf_text()

        for expected in ("ООО Евроторг", "20.08.2025", "кг", "РФ",
                         "Конфеты Южная ночь", "10", "55"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
