#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

# src/core/job_applier.py
import time

import pyautogui
from selenium.webdriver.common.by import By

from config.questions import questions_data
from config.settings import settings_data
from src.core.question_handlers.checkbox_handler import CheckboxHandler
from src.core.question_handlers.radio_handler import RadioHandler
from src.core.question_handlers.select_handler import SelectHandler
from src.core.question_handlers.text_handler import TextHandler
from src.utils.logger import logger


class JobApplier:
    def __init__(self, scraper, ai_manager, csv_manager):
        self.scraper = scraper
        self.ai = ai_manager
        self.csv = csv_manager
        self.pause_before_submit = settings_data.pause_before_submit

        self.handlers = [
            SelectHandler(scraper, ai_manager),
            RadioHandler(scraper, ai_manager),
            TextHandler(scraper, ai_manager),
            CheckboxHandler(scraper, ai_manager)
        ]

    def execute_easy_apply_flow(self, job_id, job_description):
        """Navigates through the Easy Apply modal pages."""
        try:
            modal = self.scraper.interactor.try_xpath('//div[contains(@class, "jobs-easy-apply-modal")]', click=False)
            if not modal:
                return False

            self.scraper.interactor.wait_span_click("Next", timeout=1)

            errored = ""
            questions_list = set()
            next_button = True
            next_counter = 0
            uploaded = False
            while next_button:
                next_counter += 1
                if next_counter > 10:
                    logger.error("Stuck in a loop of next buttons. Aborting application.")
                    if settings_data.pause_at_failed_question:
                        self.scraper.interactor.save_screenshot(job_id,
                                                                "Needed manual intervention for failed question")
                        pyautogui.alert(
                            "Couldn't answer one or more questions_data.\nPlease click \"Continue\" once done.\nDO NOT CLICK Back, Next or Review button in LinkedIn.\n\n\n\n\nYou can turn off \"Pause at failed question\" setting in config.py",
                            "Help Needed", "Continue")
                        next_counter = 1
                        continue
                    if questions_list: logger.error("Stuck for one or some of the following questions_data...",
                                                    questions_list)
                    self.scraper.interactor.save_screenshot(job_id, "Failed at questions")
                    errored = "stuck"
                    raise Exception("Stuck in a loop of next buttons. Aborting application.")

                # 1. Answer questions on the current page
                new_questions = self.answer_questions(modal, job_description)
                questions_list.update(new_questions)

                # 2. Upload resume if prompted
                if settings_data.uploadNewResume and not uploaded:
                    uploaded, _ = self._upload_resume(modal, questions_data.default_resume_path)

                # 3. Navigate forward (Try Review first, then Next)
                # FIX: Set click=True so it uses your human_click() method which safely handles ElementClickInterceptedException
                review_btn = self.scraper.interactor.wait_span_click("Review", timeout=1, click=True)
                if review_btn:
                    next_button = False  # Successfully clicked Review, end loop
                else:
                    next_btn = self.scraper.interactor.wait_span_click("Next", timeout=1, click=True)
                    if not next_btn:
                        next_button = False  # Neither Review nor Next found, end loop

                self.scraper.interactor.sleep_buffer(1, 2)

            # Final Screen Actions
            self._handle_follow_company(modal, settings_data.follow_companies)

            # --------
            if errored != "stuck" and self.pause_before_submit:
                decision = pyautogui.confirm(
                    '1. Please verify your information.\n2. If you edited something, please return to this final screen.\n3. DO NOT CLICK "Submit Application".\n\n\n\n\nYou can turn off "Pause before submit" setting in config.py\nTo TEMPORARILY disable pausing, click "Disable Pause"',
                    "Confirm your information", ["Enable Auto-Submit", "Discard Application", "Submit Application"])
                if decision == "Discard Application": raise Exception("Job application discarded by user!")
                self.pause_before_submit = False if "Enable Auto-Submit" == decision else True

            ## Submit Application
            # 1. Fixed the keyword argument: scroll_top=True
            submit_btn = self.scraper.interactor.wait_span_click("Submit application", timeout=2, scroll_top=True)
            if not submit_btn:
                submit_btn = self.scraper.interactor.wait_span_click("Submit", timeout=2, scroll_top=True)

            if submit_btn or (errored != "stuck" and self.pause_before_submit and "Yes" in pyautogui.confirm(
                    "You submitted the application, didn't you ??", "Failed to find Submit Application!",
                    ["Yes", "No"])):
                time.sleep(1.5)
                self._handle_post_submit_popup()
                self.scraper.interactor.wait_span_click("Done", timeout=3)
                return questions_list
            else:
                logger.warning("Since Submit Application failed, discarding the job application...")
            return False

        except Exception as e:
            logger.error(f"Error during Easy Apply flow: {e}")
            return False

    def answer_questions(self, modal, job_description):
        from selenium.common.exceptions import StaleElementReferenceException
        questions_list = set()
        num_questions = len(modal.find_elements(By.XPATH, ".//div[@data-test-form-element]"))
        for i in range(num_questions):
            try:
                current_questions = modal.find_elements(By.XPATH, ".//div[@data-test-form-element]")
                if i >= len(current_questions):
                    break
                question = current_questions[i]

                handled = False
                for handler in self.handlers:
                    if handler.can_handle(question):
                        label, answer, q_type = handler.handle(question, job_description)
                        logger.info(f'Question: {label} ==> {answer}')
                        questions_list.add((label, answer, q_type))
                        handled = True
                        break

                if not handled:
                    logger.warning(f"Encountered an unknown question type at index {i}! Skipping.")

            except StaleElementReferenceException:
                logger.warning(f"Question at index {i} went stale. LinkedIn re-rendered the DOM. Retrying or skipping.")
                continue  # Safely continue to the next question instead of crashing
            except Exception as e:
                logger.error(f"Unexpected error answering question at index {i}: {e}")

        return questions_list

    def _upload_resume(self, modal, resume_path: str) -> tuple[bool, str]:
        import os
        import time
        from selenium.webdriver.common.by import By

        try:
            # 1. Check if a resume is already uploaded or pre-selected
            # LinkedIn renders a "Remove" button or a "ui-attachment" card when a document is active.
            existing_resume = modal.find_elements(
                By.XPATH,
                ".//button[contains(@aria-label, 'Remove')] | .//div[contains(@class, 'ui-attachment')]"
            )

            # Check if a previously saved resume radio button is selected
            selected_radio = modal.find_elements(
                By.XPATH,
                ".//input[@type='radio' and @checked]"
            )

            if existing_resume or selected_radio:
                logger.info("A resume is already attached or pre-selected. Skipping upload.")
                return True, "Previous resume"

            # 2. If no resume is present, attempt to upload
            file_input = modal.find_elements(By.XPATH, ".//input[@type='file']")

            if file_input:
                file_input[0].send_keys(os.path.abspath(resume_path))
                logger.info(f"Successfully uploaded new resume from: {resume_path}")

                # Give LinkedIn's backend a moment to process the file upload
                time.sleep(1.5)
                return True, "Uploaded new resume"
            else:
                logger.debug("No file input found. Resume upload might not be required on this page.")
                return False, "No file input"

        except Exception as e:
            logger.error(f"Error during resume upload check: {e}")
            return False, "Error during upload"

    def _handle_follow_company(self, modal, follow_preference: bool):
        try:
            follow_checkbox = modal.find_element(By.XPATH,
                                                 ".//input[@id='follow-company-checkbox' and @type='checkbox']")
            if follow_checkbox.is_selected() != follow_preference:
                label = modal.find_element(By.XPATH, ".//label[@for='follow-company-checkbox']")
                self.scraper.interactor.scroll_to_view(label)
                # Safely attempt to click the label without throwing exceptions
                try:
                    self.scraper.interactor.human_click(label)
                except:
                    pass
        except:
            pass

    def _handle_post_submit_popup(self):
        """
        Handles LinkedIn post-submit popups like:
        - Update profile
        - Not now
        - Done
        - Dismiss
        """

        import time
        from selenium.webdriver.common.by import By

        try:
            time.sleep(2)

            popup_buttons = self.scraper.driver.find_elements(By.TAG_NAME, "button")

            for btn in popup_buttons:
                try:
                    text = btn.text.strip().lower()

                    if text in [
                        "not now",
                        "done",
                        "dismiss",
                        "skip"
                    ]:
                        logger.info(f"Clicking post-submit popup button: {text}")

                        self.scraper.driver.execute_script(
                            "arguments[0].click();",
                            btn
                        )

                        time.sleep(1.5)
                        return True

                except Exception:
                    continue

            # Fallback close button (X)
            close_buttons = self.scraper.driver.find_elements(
                By.XPATH,
                "//button[contains(@aria-label,'Dismiss')]"
            )

            if close_buttons:
                logger.info("Closing popup using dismiss button")

                self.scraper.driver.execute_script(
                    "arguments[0].click();",
                    close_buttons[0]
                )

                time.sleep(1.5)
                return True

        except Exception as e:
            logger.warning(f"Failed handling post-submit popup: {e}")

        return False