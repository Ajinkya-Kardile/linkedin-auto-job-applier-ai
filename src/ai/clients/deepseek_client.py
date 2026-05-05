# src/ai/clients/deepseek_client.py
import json
from openai import OpenAI
from config.secrets import secrets_data
from src.ai.prompts import deepseek_extract_skills_prompt, ai_answer_prompt
from src.utils.logger import logger
from config.questions import questions_data


class DeepSeekClient:
    def __init__(self):
        logger.info("Initializing DeepSeek Client...")

        if not secrets_data.llm_api_key or secrets_data.llm_api_key == "YOUR_API_KEY":
            raise ValueError("DeepSeek API key is missing. Please configure it in config/secrets.py")

        # Handle trailing slashes in custom URLs
        base_url = secrets_data.llm_api_url[:-1] if secrets_data.llm_api_url.endswith('/') else secrets_data.llm_api_url

        self.client = OpenAI(base_url=base_url, api_key=secrets_data.llm_api_key)
        self.model = secrets_data.llm_model

        logger.info("---- SUCCESSFULLY CREATED DEEPSEEK CLIENT! ----")
        logger.info(f"Using API URL: {base_url}")
        logger.info(f"Using Model: {self.model}")

    def extract_skills(self, job_description: str) -> dict | str:
        logger.info("-- EXTRACTING SKILLS FROM JOB DESCRIPTION [DeepSeek]")
        prompt = deepseek_extract_skills_prompt.format(job_description)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                timeout=30
            )
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return content
        except Exception as e:
            logger.error(f"DeepSeek skills extraction failed: {e}")
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
            prompt += f"\n\nJOB DESCRIPTION:\n{job_description}"

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Slight randomness recommended for DeepSeek reasoning
                timeout=30
            )
            answer = response.choices[0].message.content.strip()
            logger.debug(f"AI Response: {answer}")
            return answer
        except Exception as e:
            logger.error(f"DeepSeek failed to answer question '{question}': {e}")
            return ""

    def close(self):
        if self.client:
            logger.info("Closing DeepSeek client...")
            self.client.close()
