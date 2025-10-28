import json
import logging

from google import genai
from pydantic import BaseModel

from core.policy import Policy

logger = logging.getLogger("myapp")


class Compliance(BaseModel):
    compliance: bool
    violation_reason: str
    highlighted_text: str

class SLMWrapper:
    def __init__(self, name: str, client:genai.Client, model:str):
        self.name = name
        self.client = client  # this can be the SDK instance
        self.model = model

    async def evaluate_policy(self, policy: Policy, user_input: str, context: dict = None) -> str:
        prompt = policy(user_input, context=context)
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=[prompt],
            # config={
            #     "response_mime_type": "application/json",
            #     "response_schema": Compliance,
            # }
        )

        return policy.name, self._parse_response(response.text)


    def _parse_response(self, response: str) -> str:
        try:
            response = response[7:-3].strip()

            parsed = json.loads(response)

            logger.info(f"{self.name} --> {parsed['compliant']}, reason: {parsed['violation_reason']}")

            # Handle both string ("true"/"false") and boolean (True/False) responses
            compliant_value = parsed.get("compliant")

            # Convert to lowercase string for comparison
            if isinstance(compliant_value, bool):
                compliant_str = str(compliant_value).lower()
            else:
                compliant_str = str(compliant_value).lower()

            if compliant_str == "true":
                return "compliant"
            elif compliant_str == "false":
                return "violation"
            else:
                return "unknown"
        except (json.JSONDecodeError, AttributeError):
            return "unknown"


    async def __call__(self, policy: Policy, user_input: str, context: dict = None) -> str:
        return await self.evaluate_policy(policy, user_input, context=context)