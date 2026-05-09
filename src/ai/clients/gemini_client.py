#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

# src/ai/clients/gemini_client.py
import json

import google.generativeai as genai

from config.questions import questions_data
from config.secrets import secrets_data
from src.ai.prompts import extract_skills_prompt, ai_answer_prompt
from src.utils.logger import logger


class GeminiClient:
    def __init__(self):
        logger.info("Initializing Gemini Client...")

        if not secrets_data.llm_api_key or "YOUR_API_KEY" in secrets_data.llm_api_key:
            raise ValueError("Gemini API key is not set. Please configure it in config/secrets.py")

        genai.configure(api_key=secrets_data.llm_api_key)
        self.model = genai.GenerativeModel(secrets_data.llm_model)

        # Define relaxed safety settings for job applications to prevent false positives
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        logger.info("---- SUCCESSFULLY CONFIGURED GEMINI CLIENT! ----")
        logger.info(f"Using Model: {secrets_data.llm_model}")

    def extract_skills(self, job_description: str) -> dict | str:
        logger.info("-- EXTRACTING SKILLS FROM JOB DESCRIPTION [Gemini]")
        prompt = extract_skills_prompt.format(
            job_description) + "\n\nImportant: Respond with ONLY valid JSON, no markdown formatting."

        try:
            response = self.model.generate_content(prompt, safety_settings=self.safety_settings)

            if not response.parts:
                raise ValueError("Response was blocked by safety filters.")

            result = response.text

            # Clean Markdown if Gemini returns it despite instructions
            if result.startswith("```json"):
                result = result[7:]
            if result.endswith("```"):
                result = result[:-3]

            try:
                return json.loads(result.strip())
            except json.JSONDecodeError:
                return result.strip()

        except Exception as e:
            logger.error(f"Gemini skills extraction failed: {e}")
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
            response = self.model.generate_content(prompt, safety_settings=self.safety_settings)
            if not response.parts:
                raise ValueError("Response blocked by Gemini safety filters.")

            answer = response.text.strip()
            logger.debug(f"AI Response: {answer}")
            return answer
        except Exception as e:
            logger.error(f"Gemini failed to answer question '{question}': {e}")
            return ""

    def close(self):
        # Gemini client via google.generativeai does not require an explicit close
        pass
