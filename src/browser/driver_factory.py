#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

# src/browser/driver_factory.py
import os

from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import settings_data
from src.utils.logger import logger

if settings_data.stealth_mode:
    import undetected_chromedriver as uc
else:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options


def get_default_temp_profile():
    """Generates a path for a temporary guest profile."""
    return os.path.join(os.getcwd(), "temp_profile")


def find_default_profile_directory():
    """Locates the default Chrome profile on the user's OS."""
    app_data = os.getenv('LOCALAPPDATA')
    if app_data:
        path = os.path.join(app_data, 'Google', 'Chrome', 'User Data')
        if os.path.exists(path):
            return path
    return None


def create_driver(is_retry: bool = False):
    """
    Initializes and returns the WebDriver, ActionChains, and WebDriverWait.
    """
    options = uc.ChromeOptions() if settings_data.stealth_mode else Options()

    if settings_data.run_in_background:
        options.add_argument("--headless")
    if settings_data.disable_extensions:
        options.add_argument("--disable-extensions")

    profile_dir = find_default_profile_directory()

    if is_retry:
        logger.info("Retrying with a guest profile. Browsing history will not be saved.")
    elif profile_dir and not settings_data.safe_mode:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        logger.info("Logging in with a guest profile.")
        options.add_argument(f"--user-data-dir={get_default_temp_profile()}")

    try:
        if settings_data.stealth_mode:
            logger.info("Initializing undetected-chromedriver...")
            driver = uc.Chrome(options=options, version_main=147)
        else:
            driver = webdriver.Chrome(options=options)

        driver.maximize_window()
        wait = WebDriverWait(driver, 5)
        actions = ActionChains(driver)
        return driver, actions, wait

    except SessionNotCreatedException as e:
        if not is_retry:
            logger.error("Failed to create Chrome Session, retrying with guest profile.")
            return create_driver(is_retry=True)
        else:
            logger.critical("Fatal error creating Chrome session.", exc_info=True)
            raise e
