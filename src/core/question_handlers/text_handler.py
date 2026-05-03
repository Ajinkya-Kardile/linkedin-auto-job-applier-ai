# src/core/question_handlers/text_handler.py
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from src.core.question_handlers.base_handler import BaseQuestionHandler
from src.utils.logger import logger
import config.questions as question
import config.personals as personal


class TextHandler(BaseQuestionHandler):
    def can_handle(self, question_element):
        return (self.scraper.interactor.try_xpath('.//input[@type="text"]', click=False, element=question_element) or
                self.scraper.interactor.try_xpath('.//textarea', click=False, element=question_element))

    def handle(self, question_element, job_description):
        # 1. Identify input type
        input_element = self.scraper.interactor.try_xpath('.//input[@type="text"]', click=False,
                                                          element=question_element)
        question_type = "text"
        if not input_element:
            input_element = self.scraper.interactor.try_xpath('.//textarea', click=False, element=question_element)
            question_type = "textarea"

        # 2. Extract Label
        label_element = self.scraper.interactor.try_xpath('.//label[@for]', click=False, element=question_element)
        try:
            hidden_label = label_element.find_element(By.CLASS_NAME, 'visually-hidden')
            label_text = hidden_label.text if hidden_label else label_element.text
        except:
            label_text = label_element.text if label_element else "Unknown"

        label_lower = label_text.lower()
        prev_answer = input_element.get_attribute("value")
        answer = ""
        do_actions = False

        # 3. Match Exact Conditions from original runAiBot.py
        if not prev_answer or question.overwrite_previous_answers:
            # Textarea specifics
            if question_type == "textarea":
                if 'summary' in label_lower:
                    answer = question.linkedin_summary
                elif 'cover' in label_lower:
                    answer = question.cover_letter

            # Standard Text Input specifics
            if answer == "":
                if 'experience' in label_lower or 'years' in label_lower:
                    answer = str(question.years_of_experience)
                elif 'phone' in label_lower or 'mobile' in label_lower:
                    answer = personal.phone_number
                elif 'street' in label_lower:
                    answer = personal.street
                elif 'city' in label_lower or 'location' in label_lower or 'address' in label_lower:
                    answer = personal.current_city
                    do_actions = True
                elif 'signature' in label_lower:
                    answer = f"{personal.first_name} {personal.middle_name} {personal.last_name}"
                elif 'name' in label_lower:
                    if 'full' in label_lower:
                        answer = f"{personal.first_name} {personal.middle_name} {personal.last_name}"
                    elif 'first' in label_lower and 'last' not in label_lower:
                        answer = personal.first_name
                    elif 'middle' in label_lower and 'last' not in label_lower:
                        answer = personal.middle_name
                    elif 'last' in label_lower and 'first' not in label_lower:
                        answer = personal.last_name
                    elif 'employer' in label_lower:
                        answer = question.recent_employer
                    else:
                        answer = f"{personal.first_name} {personal.middle_name} {personal.last_name}"
                elif 'notice' in label_lower:
                    if 'month' in label_lower:
                        answer = str(question.notice_period // 30)
                    elif 'week' in label_lower:
                        answer = str(question.notice_period // 7)
                    else:
                        answer = str(question.notice_period)
                elif 'salary' in label_lower or 'compensation' in label_lower or 'ctc' in label_lower or 'pay' in label_lower:
                    if 'current' in label_lower or 'present' in label_lower:
                        if 'month' in label_lower:
                            answer = str(round(question.current_ctc / 12, 2))
                        elif 'lakh' in label_lower:
                            answer = str(round(question.current_ctc / 100000, 2))
                        else:
                            answer = str(question.current_ctc)
                    else:
                        if 'month' in label_lower:
                            answer = str(round(question.desired_salary / 12, 2))
                        elif 'lakh' in label_lower:
                            answer = str(round(question.desired_salary / 100000, 2))
                        else:
                            answer = str(question.desired_salary)
                elif 'linkedin' in label_lower:
                    answer = question.linkedIn
                elif 'website' in label_lower or 'blog' in label_lower or 'portfolio' in label_lower or 'link' in label_lower:
                    answer = question.website
                elif 'scale of 1-10' in label_lower:
                    answer = str(question.confidence_level)
                elif 'headline' in label_lower:
                    answer = question.linkedin_headline
                elif ('hear' in label_lower or 'come across' in label_lower) and 'this' in label_lower and (
                        'job' in label_lower or 'position' in label_lower):
                    answer = ""
                elif 'state' in label_lower or 'province' in label_lower:
                    answer = personal.state
                elif 'zip' in label_lower or 'postal' in label_lower or 'code' in label_lower:
                    answer = personal.zipcode
                elif 'country' in label_lower:
                    answer = personal.country

            # 4. Fallback to AI
            if answer == "" and self.ai.is_active:
                answer = self.ai.get_answer(label_text, question_type, job_description, self.user_data)

            # 5. Execute Action
            input_element.clear()
            if answer:
                input_element.send_keys(answer)
            if do_actions:
                time.sleep(2)
                self.scraper.actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

        return (label_text, input_element.get_attribute("value"), question_type)
