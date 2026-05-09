# src/ai/clients/openai_client.py
import json

from openai import OpenAI

from config.questions import questions_data
from config.secrets import secrets_data
from src.ai.prompts import extract_skills_prompt, extract_skills_response_format, ai_answer_prompt
from src.utils.logger import logger


class OpenAIClient:
    def __init__(self):
        logger.info("Initializing OpenAI Client...")

        if not secrets_data.llm_api_key or secrets_data.llm_api_key == "YOUR_API_KEY":
            raise ValueError("OpenAI API key is missing. Please configure it in config/secrets.py")

        self.client = OpenAI(base_url=secrets_data.llm_api_url, api_key=secrets_data.llm_api_key)
        self.model = secrets_data.llm_model

        try:
            # Validate if the chosen model exists in the API
            models = [m.id for m in self.client.models.list().data]
            if self.model not in models:
                raise ValueError(f"Model `{self.model}` is not found in the provided OpenAI API!")

            logger.info("---- SUCCESSFULLY CREATED OPENAI CLIENT! ----")
            logger.info(f"Using API URL: {secrets_data.llm_api_url}")
            logger.info(f"Using Model: {self.model}")
        except Exception as e:
            logger.error(f"Error validating OpenAI models: {e}")

    def extract_skills(self, job_description: str) -> dict | str:
        logger.info("-- EXTRACTING SKILLS FROM JOB DESCRIPTION [OpenAI]")
        prompt = extract_skills_prompt.format(job_description)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format=extract_skills_response_format,
                temperature=0
            )
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
        except Exception as e:
            logger.error(f"OpenAI skills extraction failed: {e}")
            return "Error extracting skills"

    def answer_question(self, question: str, question_type: str, job_description: str,
                        options: list = None) -> str:
        logger.info(f"-- ANSWERING QUESTION using AI: {question}")

        user_info_str = questions_data.linkedin_summary
        prompt = ai_answer_prompt.format(user_info_str, question)

        # Inject Options Logic
        if options and (question_type in ['select', 'radio', 'single_select', 'multiple_select']):
            options_str = "OPTIONS:\n" + "\n".join([f"- {opt}" for opt in options])
            prompt += f"\n\n{options_str}"
            if question_type in ['select', 'radio', 'single_select']:
                prompt += "\n\nPlease select exactly ONE option from the list above. Return ONLY the exact text of the option."
            else:
                prompt += "\n\nYou may select MULTIPLE options from the list above if appropriate."

        if job_description and job_description != "Unknown":
            prompt += f"\n\nJob Description:\n{job_description}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2  # Slight temperature for human-like response
            )
            answer = response.choices[0].message.content.strip()
            logger.debug(f"AI Response: {answer}")
            return answer
        except Exception as e:
            logger.error(f"OpenAI failed to answer question '{question}': {e}")
            return ""

    def close(self):
        if self.client:
            logger.info("Closing OpenAI client...")
            self.client.close()
