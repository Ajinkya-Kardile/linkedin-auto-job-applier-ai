# src/ai/ai_manager.py
from src.utils.logger import logger
from config.secrets import secrets_data

# You will move your existing logic from modules/ai/ into these client files
from src.ai.clients.openai_client import OpenAIClient
from src.ai.clients.gemini_client import GeminiClient
from src.ai.clients.deepseek_client import DeepSeekClient


class AIManager:
    def __init__(self):
        self.is_active = secrets_data.use_AI
        self.provider = secrets_data.ai_provider.lower() if secrets_data.use_AI else None
        self.client = self._initialize_client()

    def _initialize_client(self):
        if not self.is_active:
            return None

        try:
            if self.provider == "openai":
                return OpenAIClient()
            elif self.provider == "gemini":
                return GeminiClient()
            elif self.provider == "deepseek":
                return DeepSeekClient()
            else:
                logger.warning(f"Unknown AI provider '{self.provider}'. AI disabled.")
                self.is_active = False
                return None
        except Exception as e:
            logger.error(f"Failed to initialize {self.provider} client: {e}")
            self.is_active = False
            return None

    def extract_skills(self, job_description: str) -> str:
        if not self.is_active or not self.client:
            return "AI Disabled"

        try:
            logger.info(f"Extracting skills using {self.provider.upper()}...")
            return self.client.extract_skills(job_description)
        except Exception as e:
            logger.error(f"AI failed to extract skills: {e}")
            return "Error extracting skills"

    def get_answer(self, question: str, question_type: str, job_description: str) -> str:
        if not self.is_active or not self.client:
            return ""

        try:
            logger.info(f"Asking AI for answer to: '{question}'")
            answer = self.client.answer_question(question, question_type, job_description)
            logger.debug(f"AI suggested: {answer}")
            return answer
        except Exception as e:
            logger.error(f"AI failed to answer question '{question}': {e}")
            return ""

    def close(self):
        """Cleanup resources if necessary (e.g., closing sessions)."""
        if self.client and hasattr(self.client, 'close'):
            self.client.close()