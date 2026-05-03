# src/browser/scraper.py
import re
import time

import pyautogui
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException

from src.browser.interactors import DOMInteractor
from src.utils.logger import logger

# Import configurations used for filtering and blacklisting
import config.settings as settings
import config.search as search_config
from config.search import current_experience, did_masters


class LinkedInScraper:
    def __init__(self, driver, actions, wait):
        self.driver = driver
        self.actions = actions
        self.wait = wait
        self.interactor = DOMInteractor(driver, actions, wait)

        # Regex for extracting experience from job descriptions
        self.re_experience = re.compile(r'[(]?\s*(\d+)\s*[)]?\s*[-to]*\s*\d*[+]*\s*year[s]?', re.IGNORECASE)

    def is_logged_in(self) -> bool:
        if self.driver.current_url == "https://www.linkedin.com/feed/": return True
        if self.interactor.try_xpath('//button[@type="submit" and contains(text(), "Sign in")]',
                                     click=False): return False
        if self.interactor.try_link_text("Sign in"): return False
        if self.interactor.try_link_text("Join now"): return False
        return True

    def login(self, username, password):
        try:
            if not username or not password:
                pyautogui.alert(
                    "User did not configure username and password in secrets.py, hence can't login automatically! Please login manually!",
                    "Login Manually", "Okay")
                logger.warning(
                    "User did not configure username and password in secrets.py, hence can't login automatically! Please login manually!")
                self.manual_login_retry()
            else:
                self.auto_login(username, password)
                if not self.is_logged_in():
                    pyautogui.alert(
                        "Auto-login failed (Captcha?). Please login manually.",
                        "Login Manually", "Okay")
                    logger.warning("Auto-login failed (Captcha?). Please login manually.")
                    if not self.manual_login_retry():
                        logger.critical("Manual login failed. Exiting.")
        except Exception as e:
            try:
                profile_button = self.interactor.find_by_class("profile__details")
                profile_button.click()
            except Exception as e2:
                logger.error("Couldn't Login!")

    def auto_login(self, username, password):
        self.driver.get("https://www.linkedin.com/login")
        try:
            self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
            self.interactor.text_input_by_id("username", username)
            self.interactor.text_input_by_id("password", password)
            self.driver.find_element(By.XPATH, '//button[@type="submit" and contains(text(), "Sign in")]').click()
            self.wait.until(EC.url_to_be("https://www.linkedin.com/feed/"))
            logger.info("Login successful!")
        except Exception as e:
            logger.error("Login attempt failed. Manual intervention may be required.", exc_info=True)

    def manual_login_retry(self, retries=2):
        self.wait.until(EC.presence_of_element_located((By.LINK_TEXT, "Forgot password?")))
        from pyautogui import alert
        count = 0
        while not self.is_logged_in():
            logger.warning("Seems like you're not logged in!")
            button = "Confirm Login"
            message = 'After you successfully Log In, please click "{}" button below.'.format(button)
            if count > retries:
                button = "Skip Confirmation"
                message = 'If you\'re seeing this message even after you logged in, Click "{}". Seems like auto login confirmation failed!'.format(
                    button)
            count += 1
            if alert(message, "Login Required", button) and count > retries: return

    def apply_filters(self):
        """Applies location and job preferences from config."""
        # 1. Location
        if search_config.search_location.strip():
            logger.info(f"Setting location: {search_config.search_location}")
            try:
                loc_input = self.interactor.try_xpath(
                    ".//input[@aria-label='City, state, or zip code'and not(@disabled)]", click=False)
                if loc_input:
                    loc_input.send_keys(Keys.CONTROL + "a")
                    loc_input.send_keys(search_config.search_location.strip())
                    time.sleep(2)
                    loc_input.send_keys(Keys.ENTER)
            except Exception as e:
                logger.warning("Failed to update search location.")

        # 2. Open All Filters
        try:
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="All filters"]'))).click()
            self.interactor.sleep_buffer(1, 3)

            # Standard Spans
            self.interactor.wait_span_click(search_config.sort_by)
            self.interactor.wait_span_click(search_config.date_posted)

            # Multi-selects (Assuming multi_sel_noWait logic is implemented in interactor or handled here)
            for text in (search_config.experience_level + search_config.job_type
                         + search_config.on_site + search_config.location
                         + search_config.job_titles + search_config.benefits + search_config.commitments):
                self.interactor.wait_span_click(text, timeout=2, scroll=True)

            for company in search_config.companies:
                self.interactor.span_search_click("Add a company", company)

            for industry in search_config.industry:
                self.interactor.span_search_click("Add an industry", industry)

            for job in search_config.job_function:
                self.interactor.span_search_click("Add a job function", job)

            # Easy Apply Toggle
            if search_config.easy_apply_only: self.interactor.toggle_button_click("Easy Apply")
            if search_config.under_10_applicants: self.interactor.toggle_button_click("Under 10 applicants")
            if search_config.in_your_network: self.interactor.toggle_button_click("In your network")
            if search_config.fair_chance_employer: self.interactor.toggle_button_click("Fair Chance Employer")

            # Show Results
            show_results = self.driver.find_element(By.XPATH,
                                                    '//button[contains(translate(@aria-label, "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "apply current filters to show")]')
            show_results.click()
            self.interactor.sleep_buffer(2, 3)
        except Exception as e:
            logger.error(f"Failed to apply some filters: {e}")

    def get_page_info(self):
        """Returns the pagination element and current page number."""
        try:
            classes = ["jobs-search-pagination__pages", "artdeco-pagination", "artdeco-pagination__pages"]
            pagination_element = None
            for c in classes:
                try:
                    pagination_element = self.driver.find_element(By.CLASS_NAME, c)
                    break
                except:
                    continue

            if pagination_element:
                self.interactor.scroll_to_view(pagination_element)
                active_btn = pagination_element.find_element(By.XPATH, ".//button[contains(@class, 'active')]")
                return pagination_element, int(active_btn.text)
        except Exception:
            logger.debug("Failed to find Pagination element.")
        return None, None

    def go_to_next_page(self, pagination_element, current_page) -> bool:
        try:
            next_button_xpath = f".//button[@aria-label='Page {current_page + 1}']"
            next_btn = pagination_element.find_element(By.XPATH, next_button_xpath)
            self.interactor.scroll_to_view(next_btn)
            try:
                self.interactor.human_click(next_btn)
            except Exception:
                self.driver.execute_script("arguments[0].click();", next_btn)
            self.interactor.sleep_buffer(2.0, 4.0)  # Let the next page load
            return True

        except Exception as e:
            self.logger.error(f"Failed to navigate to page {current_page + 1}: {e}")
            return False

    def get_job_listings_on_page(self):
        """Waits for and returns all job list elements on the current page."""
        try:
            self.wait.until(EC.presence_of_all_elements_located((By.XPATH, "//li[@data-occludable-job-id]")))
            return self.driver.find_elements(By.XPATH, "//li[@data-occludable-job-id]")
        except Exception:
            return []

    def extract_job_card_details(self, job_element) -> dict:
        """Parses the text from a job card listing in the left pane."""
        job_details_button = job_element.find_element(By.TAG_NAME, 'a')
        self.interactor.scroll_to_view(job_details_button, top=True)

        job_id = job_element.get_attribute('data-occludable-job-id')
        title = job_details_button.text.split("\n")[0]

        try:
            other_details = job_element.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle').text
            index = other_details.find(' · ')
            company = other_details[:index] if index != -1 else other_details
            work_location_raw = other_details[index + 3:] if index != -1 else ""

            work_style = work_location_raw[work_location_raw.rfind('(') + 1:work_location_raw.rfind(
                ')')] if '(' in work_location_raw else "Unknown"
            work_location = work_location_raw[
                :work_location_raw.rfind('(')].strip() if '(' in work_location_raw else work_location_raw
        except:
            company, work_location, work_style = "Unknown", "Unknown", "Unknown"

        return {
            "job_id": job_id,
            "title": title,
            "company": company,
            "work_location": work_location,
            "work_style": work_style,
            "element_button": job_details_button
        }

    def click_job_card(self, job_element):
        """Clicks the job card to load details in the right pane."""
        try:
            btn = job_element.find_element(By.TAG_NAME, 'a')
            btn.click()
            self.interactor.sleep_buffer(2, 3)
        except:
            pass

    def get_job_description_and_check_blacklist(self) -> tuple[str, str]:
        """
        Reads the right pane. Checks about company and job description for blacklisted words.
        Returns: (job_description, skip_reason). If skip_reason is None, it is safe to apply.
        """
        try:
            # Check About Company
            about_company_org = self.driver.find_element(By.CLASS_NAME, "jobs-company__box").text.lower()
            skip_company_check = any(
                word.lower() in about_company_org for word in search_config.about_company_good_words)

            if not skip_company_check:
                for word in search_config.about_company_bad_words:
                    if word.lower() in about_company_org:
                        return "", f"Blacklisted company word found: {word}"

            # Check Job Description
            job_desc_element = self.driver.find_element(By.CLASS_NAME, "jobs-box__html-content")
            job_desc = job_desc_element.text
            job_desc_lower = job_desc.lower()

            for word in search_config.bad_words:
                if word.lower() in job_desc_lower:
                    return job_desc, f"Blacklisted job word found: {word}"

            if not search_config.security_clearance and any(
                    w in job_desc_lower for w in ['polygraph', 'clearance', 'secret']):
                return job_desc, "Requires security clearance"

            # Check Experience
            matches = re.findall(self.re_experience, job_desc)
            if matches:
                req_exp = max([int(m) for m in matches if int(m) <= 12])
                masters_bonus = 2 if did_masters and 'master' in job_desc_lower else 0
                if current_experience > -1 and req_exp > (current_experience + masters_bonus):
                    return job_desc, f"Required experience ({req_exp}) exceeds current ({current_experience})"

            return job_desc, None

        except Exception as e:
            logger.debug(f"Failed to extract full job description: {e}")
            return "Unknown", None

    def click_apply_button(self) -> bool:
        """
        Attempts to click the apply button. 
        Returns True if it's an Easy Apply (modal opens).
        Returns False if it's an External Apply (new tab opens).
        """
        is_easy_apply = self.interactor.try_xpath(
            ".//button[contains(@class,'jobs-apply-button') and contains(@class, 'artdeco-button--3') and contains(@aria-label, 'Easy')]")

        if not is_easy_apply:
            try:
                apply_btn = self.driver.find_element(By.XPATH, ".//button[contains(@class,'jobs-apply-button')]")
                tabs_before = len(self.driver.window_handles)
                apply_btn.click()
                self.interactor.sleep_buffer(1, 3)

                if len(self.driver.window_handles) > tabs_before:
                    return False  # External Apply

                # Check if modal opened
                try:
                    self.driver.find_element(By.CLASS_NAME, "jobs-easy-apply-modal")
                    return True
                except:
                    self.discard_application()
                    return False
            except:
                return False

        return bool(is_easy_apply)

    def handle_external_apply(self):
        """Handles closing the external application tab if a new one opened."""
        windows = self.driver.window_handles
        if len(windows) > 1:
            self.driver.switch_to.window(windows[-1])
            if settings.close_tabs:
                self.driver.close()
            self.driver.switch_to.window(windows[0])

    from selenium.webdriver.common.by import By

    def is_already_applied(self, job_element) -> bool:
        """Safely checks if a job is already applied to without throwing exceptions."""
        try:
            footer_states = job_element.find_elements(By.CLASS_NAME, "job-card-container__footer-job-state")
            if footer_states and "Applied" in footer_states[0].text:
                return True

            application_link_xpath = "//*[contains(@class, 'jobs-s-apply__application-link')]"
            if self.interactor.try_xpath(application_link_xpath, click=False):
                return True
            return False

        except Exception as e:
            logger.debug(f"is_already_applied check failed safely: {e}")
            return False

    def discard_application(self):
        """Cancels an ongoing easy apply application."""
        try:
            self.actions.send_keys(Keys.ESCAPE).perform()
            self.interactor.wait_span_click('Discard', timeout=2)
        except:
            pass
