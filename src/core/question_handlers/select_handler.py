# src/core/question_handlers/select_handler.py
import random
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException
from src.core.question_handlers.base_handler import BaseQuestionHandler
from src.utils.logger import logger
import config.questions as question
import config.personals as personal

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

        if question.overwrite_previous_answers or selected_option == "Select an option":
            # Match Exact Conditions
            if 'email' in label_lower or 'phone' in label_lower:
                answer = prev_answer
            elif 'gender' in label_lower or 'sex' in label_lower:
                answer = personal.gender
            elif 'disability' in label_lower:
                answer = personal.disability_status
            elif 'proficiency' in label_lower:
                answer = 'Professional'
            elif any(loc_word in label_lower for loc_word in ['location', 'city', 'state', 'country']):
                if 'country' in label_lower:
                    answer = personal.country
                elif 'state' in label_lower:
                    answer = personal.state
                elif 'city' in label_lower:
                    answer = personal.current_city
                else:
                    answer = ''
            elif 'sponsorship' in label_lower or 'visa' in label_lower:
                answer = question.require_visa

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
