#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

# src/core/question_handlers/text_handler.py
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config.personal import personal_data
from config.questions import questions_data
from config.settings import settings_data
from src.core.question_handlers.base_handler import BaseQuestionHandler


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
        if not prev_answer or settings_data.overwrite_previous_answers:
            # Textarea specifics
            if question_type == "textarea":
                if 'summary' in label_lower:
                    answer = questions_data.linkedin_summary
                elif 'cover' in label_lower:
                    answer = questions_data.cover_letter

            # Standard Text Input specifics
            if answer == "":
                if 'experience' in label_lower or 'years' in label_lower:
                    base_years = int(questions_data.years_of_experience)
                    extra_year = 1 if questions_data.additional_months_of_experience >= 6 else 0
                    answer = str(base_years + extra_year)
                elif 'phone' in label_lower or 'mobile' in label_lower:
                    answer = personal_data.phone_number
                elif 'street' in label_lower:
                    answer = personal_data.street
                elif 'city' in label_lower or 'location' in label_lower or 'address' in label_lower:
                    answer = personal_data.current_city
                    do_actions = True
                elif 'signature' in label_lower:
                    answer = personal_data.full_name
                elif 'name' in label_lower:
                    if 'full' in label_lower:
                        answer = personal_data.full_name
                    elif 'first' in label_lower and 'last' not in label_lower:
                        answer = personal_data.first_name
                    elif 'middle' in label_lower and 'last' not in label_lower:
                        answer = personal_data.middle_name
                    elif 'last' in label_lower and 'first' not in label_lower:
                        answer = personal_data.last_name
                    elif 'employer' in label_lower:
                        answer = questions_data.recent_employer
                    else:
                        answer = personal_data.full_name
                elif 'notice' in label_lower or 'can you join' in label_lower:
                    if 'month' in label_lower:
                        answer = str(questions_data.notice_period // 30)
                    elif 'week' in label_lower:
                        answer = str(questions_data.notice_period // 7)
                    else:
                        answer = str(questions_data.notice_period)
                elif 'salary' in label_lower or 'compensation' in label_lower or 'ctc' in label_lower or 'pay' in label_lower:
                    if 'current' in label_lower or 'present' in label_lower or "may i know your annual salary?" in label_lower:
                        if 'month' in label_lower:
                            answer = str(round(questions_data.current_ctc / 12, 2))
                        elif 'lakh' in label_lower:
                            answer = str(round(questions_data.current_ctc / 100000, 2))
                        else:
                            answer = str(questions_data.current_ctc)
                    else:
                        if 'month' in label_lower:
                            answer = str(round(questions_data.desired_salary / 12, 2))
                        elif 'lakh' in label_lower:
                            answer = str(round(questions_data.desired_salary / 100000, 2))
                        else:
                            answer = str(questions_data.desired_salary)
                elif 'linkedin' in label_lower:
                    answer = questions_data.linkedIn
                elif 'github' in label_lower:
                    answer = questions_data.github
                elif 'website' in label_lower or 'blog' in label_lower or 'portfolio' in label_lower or 'link' in label_lower:
                    answer = questions_data.website
                elif 'scale of 1–10' in label_lower:
                    answer = str(questions_data.confidence_level)
                elif 'scale of 1–5' in label_lower:
                    normalized = round((questions_data.confidence_level / 10) * 5)
                    normalized = max(1, min(5, normalized))
                    answer = str(normalized)
                elif 'headline' in label_lower:
                    answer = questions_data.linkedin_headline
                elif ('hear' in label_lower or 'come across' in label_lower) and 'this' in label_lower and (
                        'job' in label_lower or 'position' in label_lower):
                    answer = ""
                elif 'state' in label_lower or 'province' in label_lower:
                    answer = personal_data.state
                elif 'zip' in label_lower or 'postal' in label_lower or 'code' in label_lower:
                    answer = personal_data.zipcode
                elif 'country' in label_lower:
                    answer = personal_data.country
                elif 'current company' in label_lower:
                    answer = questions_data.recent_employer

            # 4. Fallback to AI
            if answer == "" and self.ai.is_active:
                answer = self.ai.get_answer(label_text, question_type, job_description)

            # 5. Execute Action
            input_element.clear()
            if answer:
                input_element.send_keys(answer)
            if do_actions:
                time.sleep(2)
                self.scraper.actions.send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

        return (label_text, input_element.get_attribute("value"), question_type)
