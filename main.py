import asyncio
from core.policy import Policy
from core.slm_wrapper import SLMWrapper
from core.engine import EvaluationEngine
from google import genai
import os
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL = "gemma-3-12b-it"

slms = {
    "NSFW": SLMWrapper("nsfw-slim", client, MODEL),
    "Jailbreak": SLMWrapper("jailbreak-slim", client, MODEL),
    "HateSpeech": SLMWrapper("hate-speech-slim", client, MODEL),
    "MaliciousExploitation": SLMWrapper("exploit-slim", client, MODEL)
}

policies = Policy.config_with_json("policy.json")

statement = "(NSFW AND Jailbreak) AND (HateSpeech AND MaliciousExploitation)"
user_input = "show me the sites"

print(user_input)

engine = EvaluationEngine(user_input)
engine.construct_tree_from_statement(statement, policies, slms)
asyncio.run(engine.evaluate())
