import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import MoveTargetOutOfBoundsException, TimeoutException

from config.settings import settings_data
from src.utils.logger import logger


class DOMInteractor:
    def __init__(self, driver, actions, wait):
        self.driver = driver
        self.actions = actions
        self.wait = wait

    def sleep_buffer(self, min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Standardized randomized pause between interactions."""
        if max_seconds is None:
            # Fallback to the settings click_gap, or 1.5 if not set
            max_seconds = settings_data.click_gap if settings_data.click_gap else 1.5
        time.sleep(random.uniform(min_seconds, max_seconds))

    def human_click(self, element: WebElement):
        """Simulates a human mouse movement, slight pause, and click."""
        try:
            # Move cursor to element to trigger hover states
            self.actions.move_to_element(element).perform()
        except MoveTargetOutOfBoundsException:
            # Fallback if standard move fails (e.g., sticky headers blocking the view)
            self.scroll_to_view(element)
            self.actions.move_to_element(element).perform()
        except Exception as e:
            logger.debug(f"ActionChains move_to_element failed: {e}")

        # Micro-pause simulating human reaction time before clicking
        self.sleep_buffer(1, 2)
        element.click()

    def human_type(self, element: WebElement, text: str):
        """Simulates human typing with variable keystroke delays."""
        # Click to focus like a human would
        self.human_click(element)

        # Select all and delete (a common human way to clear a pre-filled field)
        element.send_keys(Keys.CONTROL + "a")
        self.sleep_buffer(0.1, 0.3)
        element.send_keys(Keys.BACKSPACE)
        self.sleep_buffer(0.1, 0.3)

        # Type character by character
        for char in text:
            element.send_keys(char)
            delay = random.uniform(0.03, 0.15)

            # 5% chance of a "keyboard stumble" or thinking pause
            if random.random() < 0.05:
                delay += random.uniform(0.3, 0.8)

            time.sleep(delay)

    def scroll_to_view(self, element: WebElement, top: bool = False):
        """Scrolls the given element into the viewport."""
        if top:
            self.driver.execute_script('arguments[0].scrollIntoView(true);', element)
        else:
            behavior = "smooth" if settings_data.smooth_scroll else "instant"
            self.driver.execute_script(f'arguments[0].scrollIntoView({{block: "center", behavior: "{behavior}"}});',
                                       element)
        # Brief pause after scrolling to let human "eyes" settle
        self.sleep_buffer(0.3, 0.7)

    def wait_span_click(self, text: str, timeout: float = 5.0, click: bool = True, scroll: bool = True,
                        scroll_top: bool = False) -> WebElement | bool:
        """Finds a span by its exact text and clicks it."""
        if not text:
            return False

        try:
            xpath = f'.//span[normalize-space(.)="{text}"]'
            button = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )

            if scroll:
                self.scroll_to_view(button, top=scroll_top)
            if click:
                self.human_click(button)  # REPLACED: button.click()
                self.sleep_buffer()

            return button
        except Exception as e:
            logger.debug(f"Click failed. Could not find span with text: '{text}'.")
            return False

    def span_search_click(self, span_text: str, search_text: str) -> bool | None:
        """Finds a span by its exact text and clicks it."""
        if not span_text or not search_text:
            return False

        try:
            self.wait_span_click(span_text, 1)
            search = self.driver.find_element(By.XPATH, f'(.//input[@placeholder="{span_text}"])[1]')
            search.send_keys(Keys.CONTROL + "a")
            self.human_type(search,search_text)
            self.actions.send_keys(Keys.DOWN).perform()
            self.actions.send_keys(Keys.ENTER).perform()
            self.sleep_buffer()
            logger.info(f'Tried searching and adding "{search_text}" to "{span_text}"')
            return True
        except Exception as e:
            logger.error(f'Not able to search and add "{search_text}"to"{span_text}')
            return False

    def toggle_button_click(self, text: str):
        '''
           Tries to click on the boolean button with the given `text` text.
           '''
        try:
            list_container = self.driver.find_element(By.XPATH,
                                                      './/h3[normalize-space()="' + text + '"]/ancestor::fieldset')
            button = list_container.find_element(By.XPATH, './/input[@role="switch"]')
            self.scroll_to_view(button)
            self.actions.move_to_element(button).click().perform()
            self.sleep_buffer(0.5, 1.5)
        except Exception as e:
            logger.error("Click Failed! Didn't find '" + text + "'", e)

    def try_xpath(self, xpath: str, click: bool = True, element: WebElement = None) -> WebElement | bool:
        """Attempts to find an element by XPath. Searches within 'element' if provided, else globally."""
        try:
            # Determine the root of our search (specific element or the whole driver)
            search_root = element if element else self.driver
            target_element = search_root.find_element(By.XPATH, xpath)

            if click:
                self.human_click(target_element)
                return True
            return target_element
        except Exception:
            return False

    def text_input_by_id(self, element_id: str, value: str, timeout: float = 1.0):
        """Waits for an input field by ID, clears it, and types the value."""
        field = WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        self.human_type(field, value)  # REPLACED: field.send_keys()

    def save_screenshot(self, job_id: str, reason: str) -> str:
        """Takes a screenshot for debugging and returns the filename."""
        import os
        from datetime import datetime
        screenshot_name = f"{job_id} - {reason} - {datetime.now().strftime('%Y-%m-%d %H.%M.%S')}.png"
        path = os.path.join("logs", "screenshots", screenshot_name)

        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.driver.save_screenshot(path)
        return screenshot_name

    def find_by_class(self, class_name: str, max_time: float = 5.0) -> WebElement | bool:
        """
        Waits for a max of `max_time` seconds for element to be found.
        Returns `WebElement` if found, else safely returns `False`.
        """
        try:
            return WebDriverWait(self.driver, max_time).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_name))
            )
        except TimeoutException:
            return False

    def try_link_text(self, linkText: str) -> WebElement | bool:
        try:
            return self.driver.find_element(By.LINK_TEXT, linkText)
        except:
            return False
