#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

# main.py
import pyautogui

from src.browser.driver_factory import create_driver
from src.browser.scraper import LinkedInScraper
from src.ai.ai_manager import AIManager
from src.data.csv_manager import CSVManager
from src.core.bot_engine import BotEngine
from src.utils.logger import logger

# Import your configurations
from config.secrets import secrets_data


def main():
    logger.info("Initializing LinkedIn Auto Applier...")

    # 1. Setup Infrastructure Layers
    driver, actions, wait = create_driver()
    scraper = LinkedInScraper(driver, actions, wait)
    csv_manager = CSVManager()
    ai_manager = AIManager()

    # 2. Login to LinkedIn
    try:
        scraper.driver.get("https://www.linkedin.com/login")
        if not scraper.is_logged_in():
            scraper.login(secrets_data.username, secrets_data.password)

        if scraper.is_logged_in(): logger.info("Login Successful!")
    except Exception:
        logger.critical("Failed to initialize browser or login.", exc_info=True)
        return

    # 3. Inject dependencies into Core Engine and Run
    bot = BotEngine(
        scraper=scraper,
        ai_manager=ai_manager,
        csv_manager=csv_manager,
    )

    try:
        bot.start()
    finally:
        # Cleanup
        ai_manager.close()
        try:
            driver.quit()
            logger.info("Browser closed successfully.")
        except:
            pass


if __name__ == "__main__":
    main()
