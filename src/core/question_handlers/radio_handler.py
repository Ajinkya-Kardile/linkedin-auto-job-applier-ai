# src/core/question_handlers/radio_handler.py
from selenium.webdriver.common.by import By

from config.personal import personal_data
from config.questions import questions_data
from config.settings import settings_data
from src.core.question_handlers.base_handler import BaseQuestionHandler


class RadioHandler(BaseQuestionHandler):
    def can_handle(self, question_element):
        return self.scraper.interactor.try_xpath(
            './/fieldset[@data-test-form-builder-radio-button-form-component="true"]', click=False,
            element=question_element)

    def handle(self, question_element, job_description):
        radio_fieldset = self.scraper.interactor.try_xpath(
            './/fieldset[@data-test-form-builder-radio-button-form-component="true"]', click=False,
            element=question_element)

        label_element = self.scraper.interactor.try_xpath(
            './/span[@data-test-form-builder-radio-button-form-component__title]', click=False, element=radio_fieldset)
        try:
            hidden = label_element.find_element(By.CLASS_NAME, "visually-hidden")
            label_text = hidden.text if hidden else label_element.text
        except:
            label_text = label_element.text if label_element else "Unknown"

        label_lower = label_text.lower()
        options = radio_fieldset.find_elements(By.TAG_NAME, 'input')
        options_labels = []
        prev_answer = None

        for option in options:
            opt_id = option.get_attribute("id")
            opt_label = self.scraper.interactor.try_xpath(f'.//label[@for="{opt_id}"]', click=False,
                                                          element=radio_fieldset)
            label_str = opt_label.text if opt_label else "Unknown"
            options_labels.append(label_str)
            if option.is_selected():
                prev_answer = label_str

        answer = 'Yes'

        if settings_data.overwrite_previous_answers or prev_answer is None:
            # Exact mapping
            if 'citizenship' in label_lower or 'employment eligibility' in label_lower:
                answer = questions_data.us_citizenship
            elif 'veteran' in label_lower or 'protected' in label_lower:
                answer = personal_data.veteran_status
            elif 'disability' in label_lower or 'handicapped' in label_lower:
                answer = personal_data.disability_status
            elif 'sponsorship' in label_lower or 'visa' in label_lower:
                answer = questions_data.require_visa
            elif 'relationship' in label_lower:
                answer = "No"
            elif 'applied' in label_lower:
                answer = "No"

            # Find and click correct option
            found_option = self.scraper.interactor.try_xpath(f".//label[normalize-space()='{answer}']", click=False,
                                                             element=radio_fieldset)

            if found_option:
                self.scraper.actions.move_to_element(found_option).click().perform()
            else:
                possible_phrases = ["Decline", "not wish", "don't wish", "Prefer not",
                                    "not want", "No"] if answer == 'Decline' else [answer]
                ele_to_click = options[0]

                for phrase in possible_phrases:
                    for i, opt_lbl in enumerate(options_labels):
                        if phrase.lower() in opt_lbl.lower():
                            ele_to_click = options[i]
                            break

                self.scraper.actions.move_to_element(ele_to_click).click().perform()

        # Re-check selected answer
        final_answer = next((opt_label for opt, opt_label in zip(options, options_labels) if opt.is_selected()),
                            "Unknown")
        return (label_text, final_answer, "radio")
