# src/core/question_handlers/base_handler.py
from abc import ABC, abstractmethod
from selenium.webdriver.remote.webelement import WebElement


class BaseQuestionHandler(ABC):
    def __init__(self, scraper, ai_manager):
        self.scraper = scraper
        self.ai = ai_manager

    @abstractmethod
    def can_handle(self, question_element: WebElement) -> bool:
        """Returns True if this handler knows how to fill this specific HTML element."""
        pass

    @abstractmethod
    def handle(self, question_element: WebElement, job_description: str) -> tuple[str, str, str]:
        """Fills the form and returns (label, answer, type)."""
        pass