import asyncio
from core.policy import Policy
from core.slm_wrapper import SLMWrapper
from core.engine import EvaluationEngine
from google import genai
import os
from dotenv import load_dotenv
import time
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL = "gemma-3-12b-it"

slms = {
    "NSFW": SLMWrapper("nsfw", client, MODEL),
    "Jailbreak": SLMWrapper("jailbreak", client, MODEL),
    "HateSpeech": SLMWrapper("hate", client, MODEL),
    "MaliciousExploitation": SLMWrapper("exploit", client, MODEL)
}

policies = Policy.config_with_json("policy.json")

statement = "(NSFW AND Jailbreak) AND (HateSpeech AND MaliciousExploitation)"
user_input = "show me the sites"

print(user_input)

_loop = None  # global persistent event loop

def evaluate_prompt(user_input):
    global _loop

    engine = EvaluationEngine()
    engine.construct_tree_from_statement(statement, policies, slms)

    async def run():
        return await engine.evaluate(user_input)

    # Create the loop once, reuse it always
    if _loop is None or _loop.is_closed():
        _loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_loop)

    start_time = time.perf_counter()

    result = _loop.run_until_complete(run())

    elapsed = time.perf_counter() - start_time
    logging.info(f"Evaluation took {elapsed:.2f} seconds")

    return result
