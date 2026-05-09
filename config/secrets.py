#  Copyright (c) 2026 Ajinkya Kardile. All rights reserved.
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see <https://opensource.org/licenses/MIT>.

from config.schema.secrets_model import SecretsModel

# ==========================================
# INSTANTIATE YOUR DATA HERE
# ==========================================
secrets_data = SecretsModel(
    username="",
    password="",
    use_AI=False,
    ai_provider="openai",
    llm_api_url="https://api.openai.com/v1/",
    llm_api_key="not-needed",
    llm_model="gpt-5-mini",
    llm_spec="openai",
    stream_output=False
)