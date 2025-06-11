from core.prompt import MASTER_PROMPT
import json

class Policy:
    def __init__(self, name: str, alias: str, instruction: str):
        self.name = name
        self.alias = alias
        self.instruction = instruction

    def __call__(self, user_input: str) -> str:
        return MASTER_PROMPT.format(
                    policy_instruction=self.instruction,
                    text_to_check=user_input
                )
    
    def __repr__(self):
        return f"Policy: {self.name}"
    
    def config_with_json(filename)-> dict[str, "Policy"]:
        with open(filename,"r+") as file:
            policies = json.load(file)["policies"]
    
        config = {
            policy["alias"]: Policy(policy["name"], policy["alias"], policy["policy_instruction"])
            for _, policy in policies.items()
        }

        return config