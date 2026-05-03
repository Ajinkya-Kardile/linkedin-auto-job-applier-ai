# src/core/bot_engine.py
import time
import traceback
from datetime import datetime

import pyautogui
from selenium.common.exceptions import NoSuchWindowException, WebDriverException, ElementClickInterceptedException

from src.utils.logger import logger
from src.core.job_applier import JobApplier
import config.settings as settings
import config.search as search_config


class BotEngine:
    def __init__(self, scraper, ai_manager, csv_manager, user_data):
        self.scraper = scraper
        self.ai = ai_manager
        self.csv = csv_manager
        self.job_applier = JobApplier(scraper, ai_manager, csv_manager, user_data)

        # Tracking Metrics
        self.total_runs = 1
        self.easy_applied_count = 0
        self.external_jobs_count = 0
        self.failed_count = 0
        self.skip_count = 0
        self.daily_limit_reached = False

        # State
        self.applied_jobs = self.csv.get_applied_job_ids()
        self.rejected_jobs = set()
        self.blacklisted_companies = set()

        # temp setting
        self.pause_after_filters = True

    def start(self):
        """The main entry point for the bot execution."""
        logger.info(f"Starting LinkedIn Auto Applier. Cycle {self.total_runs}")

        try:
            self._run_cycle()

            while settings.run_non_stop:
                if self.daily_limit_reached:
                    logger.warning("Daily limit reached. Stopping continuous run.")
                    break

                # Cycle logic from original script
                if settings.cycle_date_posted:
                    self._cycle_date_settings()
                if settings.alternate_sortby:
                    settings.sort_by = "Most recent" if search_config.sort_by == "Most relevant" else "Most relevant"
                    self._run_cycle()
                    settings.sort_by = "Most recent" if search_config.sort_by == "Most relevant" else "Most relevant"

                self._run_cycle()

        except (NoSuchWindowException, WebDriverException):
            logger.error("Browser closed or session invalid. Exiting.", exc_info=True)
        except Exception:
            logger.critical("Fatal error in main execution loop.", exc_info=True)
        finally:
            self.print_summary()

    def _run_cycle(self):
        """Executes one complete search and apply cycle."""
        if self.daily_limit_reached:
            return

        logger.info("==================================================")
        logger.info(f"Date and Time: {datetime.now()}")
        logger.info(f"Cycle number: {self.total_runs}")

        # Iterate over all search terms
        search_terms = search_config.search_terms
        if search_config.randomize_search_order:
            import random
            random.shuffle(search_terms)

        for term in search_terms:
            if self.daily_limit_reached:
                break
            self._process_search_term(term)

        self.total_runs += 1

        if not self.daily_limit_reached:
            logger.info("Sleeping for 5 minutes before next phase...")
            time.sleep(300)

    def _process_search_term(self, search_term: str):
        """Searches for a specific term and navigates through pages."""
        logger.info(f"Searching for: '{search_term}'")
        self.scraper.driver.get(f"https://www.linkedin.com/jobs/search/?keywords={search_term}")

        # Apply filters via scraper
        self.scraper.apply_filters()
        if self.pause_after_filters and "Turn off Pause after search" == pyautogui.confirm(
                "These are your configured search results and filter. It is safe to change them while this dialog is open, any changes later could result in errors and skipping this search run.",
                "Please check your results", ["Turn off Pause after search", "Look's good, Continue"]):
            self.pause_after_filters = False

        current_count = 0
        while current_count < search_config.switch_number:
            job_listings = self.scraper.get_job_listings_on_page()
            pagination_element, current_page = self.scraper.get_page_info()

            for job_element in job_listings:
                if current_count >= search_config.switch_number or self.daily_limit_reached:
                    break
                if settings.keep_screen_awake: pyautogui.press('shiftright')
                success = self._process_single_job(job_element)
                if success:
                    current_count += 1

            # Go to next page
            if not pagination_element or not self.scraper.go_to_next_page(pagination_element, current_page):
                logger.info("No more pages available for this search term.")
                break

    def _process_single_job(self, job_element) -> bool:
        """Processes a single job card. Returns True if applied successfully."""
        from datetime import datetime
        if settings.keep_screen_awake: pyautogui.press('shiftright')
        details = self.scraper.extract_job_card_details(job_element)
        job_id = details.get('job_id')
        self.scraper.click_job_card(job_element)

        if job_id in self.applied_jobs or job_id in self.rejected_jobs or self.scraper.is_already_applied(
                job_element) or details.get(
                'company') in self.blacklisted_companies:
            logger.info(f"Skipping job {job_id} (Already processed/blacklisted)")
            self.skip_count += 1
            return False

        job_desc, skip_reason = self.scraper.get_job_description_and_check_blacklist()
        if skip_reason:
            logger.info(f"Skipping job {job_id}: {skip_reason}")
            self.rejected_jobs.add(job_id)
            self.skip_count += 1
            self.csv.log_failed_job({'Job ID': job_id, 'Assumed Reason': skip_reason})
            return False

        skills_required = self.ai.extract_skills(job_desc) if self.ai.is_active else "AI Disabled"

        try:
            is_easy_apply = self.scraper.click_apply_button()

            if is_easy_apply:
                questions_list = self.job_applier.execute_easy_apply_flow(job_id, job_desc)
                if questions_list is not False:  # Flow succeeded
                    self.easy_applied_count += 1
                    self.applied_jobs.add(job_id)

                    # Properly formatted dictionary for CSV
                    self.csv.log_submitted_job({
                        'Job ID': job_id,
                        'Title': details.get('title', 'Unknown'),
                        'Company': details.get('company', 'Unknown'),
                        'Work Location': details.get('work_location', 'Unknown'),
                        'Work Style': details.get('work_style', 'Unknown'),
                        'About Job': job_desc,
                        'Experience required': 'Unknown',
                        'Skills required': str(skills_required),
                        'HR Name': 'Unknown',
                        'HR Link': 'Unknown',
                        'Resume': 'Default Resume',
                        'Re-posted': False,
                        'Date Posted': 'Unknown',
                        'Date Applied': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'Job Link': f"https://www.linkedin.com/jobs/view/{job_id}",
                        'External Job link': 'Easy Applied',
                        'Questions Found': str(questions_list),
                        'Connect Request': 'In Development'
                    })
                else:
                    self.failed_count += 1
            # else:
            #     self.scraper.handle_external_apply()
            #     self.external_jobs_count += 1
            #     self.applied_jobs.add(job_id)
            #     # --- NEW: Log External Jobs to the CSV ---
            #     self.csv.log_submitted_job({
            #         'Job ID': job_id,
            #         'Title': details.get('title', 'Unknown'),
            #         'Company': details.get('company', 'Unknown'),
            #         'Work Location': details.get('work_location', 'Unknown'),
            #         'Work Style': details.get('work_style', 'Unknown'),
            #         'About Job': job_desc,
            #         'Experience required': 'Unknown',
            #         'Skills required': str(skills_required),
            #         'HR Name': 'Unknown',
            #         'HR Link': 'Unknown',
            #         'Resume': 'Not Applied',
            #         'Re-posted': False,
            #         'Date Posted': 'Unknown',
            #         'Date Applied': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            #         'Job Link': f"https://www.linkedin.com/jobs/view/{job_id}",
            #         'External Job link': 'External Application',
            #         'Questions Found': 'None',
            #         'Connect Request': 'N/A'
            #     })

            return True

        except Exception as e:
            logger.error(f"Failed to apply to {job_id}: {e}")
            self.failed_count += 1
            self.scraper.discard_application()
            return False

    def _cycle_date_settings(self):
        """Rotates the date_posted filter for continuous runs."""
        date_options = ["Any time", "Past month", "Past week", "Past 24 hours"]
        current_idx = date_options.index(search_config.date_posted)
        next_idx = current_idx + 1 if current_idx + 1 < len(date_options) else 0
        settings.date_posted = date_options[next_idx]

    def print_summary(self):
        """Prints the final summary when the bot stops."""
        summary = (
            f"Total runs: {self.total_runs}\n"
            f"Jobs Easy Applied: {self.easy_applied_count}\n"
            f"External job links collected: {self.external_jobs_count}\n"
            f"Total applied/collected: {self.easy_applied_count + self.external_jobs_count}\n"
            f"Failed jobs: {self.failed_count}\n"
            f"Irrelevant jobs skipped: {self.skip_count}\n"
        )
        logger.info("\n=== BOT EXECUTION SUMMARY ===\n" + summary)
