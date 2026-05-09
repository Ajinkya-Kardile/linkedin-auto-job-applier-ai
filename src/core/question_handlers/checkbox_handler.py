# src/core/question_handlers/checkbox_handler.py
from src.core.question_handlers.base_handler import BaseQuestionHandler
from src.utils.logger import logger


class CheckboxHandler(BaseQuestionHandler):
    def can_handle(self, question_element):
        return self.scraper.interactor.try_xpath('.//input[@type="checkbox"]', click=False, element=question_element)

    def handle(self, question_element, job_description):
        checkbox = self.scraper.interactor.try_xpath('.//input[@type="checkbox"]', click=False,
                                                     element=question_element)

        label_element = self.scraper.interactor.try_xpath('.//span[@class="visually-hidden"]', click=False,
                                                          element=question_element)
        label_text = label_element.text if label_element else "Unknown"

        answer_element = self.scraper.interactor.try_xpath('.//label[@for]', click=False, element=question_element)
        answer_text = answer_element.text if answer_element else "Unknown"

        is_checked = checkbox.is_selected()

        # Default behavior: always check the box if it isn't already checked
        # (usually these are "I agree to terms" or "I acknowledge")
        if not is_checked:
            try:
                self.scraper.actions.move_to_element(checkbox).click().perform()
                is_checked = True
            except Exception as e:
                logger.error(f"Failed to check checkbox for {label_text}. Error: {e}")

        return (f"{label_text} [{answer_text}]", is_checked, "checkbox")
