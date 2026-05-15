#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

# src/ai/clients/ollama_client.py
import json
import ollama

from config.questions import questions_data
from config.secrets import secrets_data
from src.ai.prompts import extract_skills_prompt, ai_answer_prompt
from src.utils.logger import logger


class OllamaClient:
    def __init__(self):
        """
        Initializes the native Ollama client for local model execution.
        """
        logger.info("Initializing Native Ollama Client...")
        self.model = secrets_data.llm_model

        try:
            # Check if the Ollama service is running and the model is downloaded
            models_response = ollama.list()
            available_models = [m['name'] for m in models_response.get('models', [])]

            # Ollama sometimes appends ':latest' to model names
            if self.model not in available_models and f"{self.model}:latest" not in available_models:
                logger.warning(f"Model `{self.model}` not found! Run 'ollama run {self.model}' in terminal.")
            else:
                logger.info("---- SUCCESSFULLY CONNECTED TO NATIVE OLLAMA! ----")
                logger.info(f"Active Model: {self.model}")

        except Exception as e:
            logger.error(f"Failed to connect to Ollama. Is 'ollama serve' running? Error: {e}")

    def extract_skills(self, job_description: str) -> dict | str:
        logger.info("-- EXTRACTING SKILLS FROM JD [Native Ollama]")
        prompt = extract_skills_prompt.format(job_description)
        logger.info(f"generated prompt: {prompt}")

        try:
            # Native format='json' forces the model to output a strict JSON structure
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                format='json',
                options={
                    "temperature": 0,
                    "num_thread": 2  # Restricts to 2 threads to keep your OS responsive
                }
            )

            content = response.get('response', '').strip()

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                logger.warning("LLM returned malformed JSON. Returning raw string.")
                return content

        except Exception as e:
            logger.error(f"Native Ollama skills extraction failed: {e}")
            return "Error extracting skills"

    def answer_question(self, question: str, question_type: str, job_description: str,
                        options: list = None) -> str:
        logger.info(f"-- GENERATING ANSWER for: {question[:50]}...")

        user_info_str = questions_data.linkedin_summary
        prompt = ai_answer_prompt.format(user_info_str, question)

        if options and (question_type in ['select', 'radio', 'single_select', 'multiple_select']):
            options_str = "AVAILABLE OPTIONS:\n" + "\n".join([f"- {opt}" for opt in options])
            prompt += f"\n\n{options_str}\n\nTask: Select the most accurate option from the list above based on my profile. Return ONLY the exact text of the option."

        if job_description and job_description != "Unknown":
            prompt += f"\n\nContext - Job Description:\n{job_description}"

        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert career assistant. Be concise and professional."},
                    {"role": "user", "content": prompt}
                ],
                options={
                    "temperature": 0.2,
                    "num_thread": 2  # Restricts to 2 threads
                }
            )

            answer = response.get('message', {}).get('content', '').strip()
            logger.debug(f"AI Answer: {answer}")
            return answer

        except Exception as e:
            logger.error(f"Native Ollama failed to answer question '{question}': {e}")
            return ""

    def close(self):
        # Native Ollama python library is stateless and doesn't require closing sessions
        pass