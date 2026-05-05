# src/core/question_handlers/select_handler.py
import random

from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from src.core.question_handlers.base_handler import BaseQuestionHandler
from src.utils.logger import logger
from config.questions import questions_data
from config.personal import personal_data
from config.settings import settings_data

class SelectHandler(BaseQuestionHandler):
    def can_handle(self, question_element):
        return self.scraper.interactor.try_xpath('.//select', click=False, element=question_element)

    def handle(self, question_element, job_description):
        select_element = self.scraper.interactor.try_xpath('.//select', click=False, element=question_element)
        select_obj = Select(select_element)

        label_element = self.scraper.interactor.try_xpath('.//label', click=False, element=question_element)
        try:
            label_text = label_element.find_element(By.TAG_NAME, "span").text
        except:
            label_text = label_element.text if label_element else "Unknown"

        label_lower = label_text.lower()
        selected_option = select_obj.first_selected_option.text
        options_text = [option.text for option in select_obj.options]

        answer = 'Yes'
        prev_answer = selected_option

        if settings_data.overwrite_previous_answers or selected_option == "Select an option":
            # Match Exact Conditions
            if 'email' in label_lower or 'phone' in label_lower:
                answer = prev_answer
            elif 'gender' in label_lower or 'sex' in label_lower:
                answer = personal_data.gender
            elif 'disability' in label_lower:
                answer = personal_data.disability_status
            elif 'proficiency' in label_lower:
                answer = 'Professional'
            elif 'experience' in label_lower:
                if 'years' in label_lower:
                    answer = str(questions_data.years_of_experience)
                elif 'additional months' in label_lower:
                    answer = str(questions_data.additional_months_of_experience)
            elif any(loc_word in label_lower for loc_word in ['location', 'city', 'state', 'country']):
                if 'country' in label_lower:
                    answer = personal_data.country
                elif 'state' in label_lower:
                    answer = personal_data.state
                elif 'city' in label_lower:
                    answer = personal_data.current_city
                else:
                    answer = personal_data.current_city
            elif 'sponsorship' in label_lower or 'visa' in label_lower:
                answer = questions_data.require_visa
            elif 'personal relationship' in label_lower:
                answer = "no"
            elif 'shareholder' in label_lower:
                answer = "no"
            elif 'salary' in label_lower or 'compensation' in label_lower or 'ctc' in label_lower or 'pay' in label_lower:
                if 'current' in label_lower or 'present' in label_lower:
                    if 'month' in label_lower:
                        answer = str(round(questions_data.current_ctc / 12))
                    elif 'lakh' in label_lower or 'lpa' in label_lower:
                        answer = str(round(questions_data.current_ctc / 100000))
                    else:
                        answer = str(questions_data.current_ctc)
                else:
                    if 'month' in label_lower:
                        answer = str(round(questions_data.desired_salary / 12, 2))
                    elif 'lakh' in label_lower or 'lpa' in label_lower:
                        answer = str(round(questions_data.desired_salary / 100000, 2))
                    else:
                        answer = str(questions_data.desired_salary)

            # Try to select the answer
            try:
                select_obj.select_by_visible_text(answer)
            except NoSuchElementException:
                # Fuzzy Matching Logic
                possible_answer_phrases = [answer, answer.lower(), answer.upper(),
                                           ''.join(c for c in answer if c.isalnum())]
                if answer == 'Decline':
                    possible_answer_phrases += ["Decline", "not wish", "don't wish", "Prefer not", "not want"]
                elif 'yes' in answer.lower():
                    possible_answer_phrases += ["Yes", "Agree", "I do", "I have"]
                elif 'no' in answer.lower():
                    possible_answer_phrases += ["No", "Disagree", "I don't", "I do not"]

                found_option = False
                for phrase in possible_answer_phrases:
                    for option in options_text:
                        if phrase.lower() in option.lower() or option.lower() in phrase.lower():
                            select_obj.select_by_visible_text(option)
                            answer = option
                            found_option = True
                            break
                    if found_option: break

                # Random Fallback if completely unknown
                if not found_option and len(select_obj.options) > 1:
                    logger.warning(f"Failed to find match for dropdown '{label_text}'. Selecting randomly.")
                    select_obj.select_by_index(random.randint(1, len(select_obj.options) - 1))
                    answer = select_obj.first_selected_option.text

        return (label_text, select_obj.first_selected_option.text, "select")
