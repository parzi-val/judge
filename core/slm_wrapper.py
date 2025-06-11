from core.policy import Policy
import json
from google import genai
from pydantic import BaseModel


class Compliance(BaseModel):
    compliance: bool
    violation_reason: str
    highlighted_text: str

class SLMWrapper:
    def __init__(self, name: str, client:genai.Client, model:str):
        self.name = name
        self.client = client  # this can be the SDK instance
        self.model = model

    async def evaluate_policy(self, policy: Policy, user_input: str) -> str:
        prompt = policy(user_input)
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
            print(self.name, parsed)
            if parsed.get("compliant") == "true":
                return "compliant"
            elif not parsed.get("compliant") == "false":
                return "violation"
            else:
                return "unknown"
        except (json.JSONDecodeError, AttributeError):
            return "unknown"


    async def __call__(self, policy: Policy, user_input: str) -> str:
        return await self.evaluate_policy(policy, user_input)