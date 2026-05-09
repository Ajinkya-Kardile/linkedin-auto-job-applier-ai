#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

from pydantic import BaseModel
from typing import Literal


class SecretsModel(BaseModel):
    username: str = ""
    password: str = ""

    use_AI: bool = False
    ai_provider: Literal["openai", "deepseek", "gemini"] = "openai"
    llm_api_url: str = "https://api.openai.com/v1/"
    llm_api_key: str = "not-needed"
    llm_model: str = "gpt-5-mini"
    llm_spec: Literal["openai", "openai-like", "openai-like-github", "openai-like-mistral"] = "openai"
    stream_output: bool = False
