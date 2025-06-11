# Judge

**Judge** is a guardrail system designed to evaluate user prompts against safety policies using Small Language Models (SLMs). It parses logical policy expressions, invokes SLMs for evaluation, and determines if a prompt is compliant or in violation.

## Features

- Logical policy expression parser (supports AND, OR, NOT)
- Evaluation tree using SLMs per policy
- Super-efficient async architecture
- Fully parallelized evaluation across models
- Modular design with reusable event loop for async inference
- Streamlit-based UI for interactive usage

## Structure

- `core/engine.py` - Builds and evaluates the logical tree
- `core/slm_wrapper.py` - Unified wrapper for SLM calls
- `core/policy.py` - Policy loader and config parser
- `main.py` - Entrypoint for backend evaluation
- `app.py` - Streamlit app for prompt evaluation and policy testings

## Usage

1. Define policies in `policy.json`.
2. Update the logical statement (e.g., `(NSFW AND Jailbreak) AND (HateSpeech AND MaliciousExploitation)`)
3. Run the Streamlit app:

```bash
streamlit run app.py
```

4. Interact with the chat UI and view evaluation results live.

## Notes

- Designed for real-time guardrail enforcement using multiple lightweight models.
- Modular enough to swap out models or add more policies easily.
- Highly optimized for low-latency policy checking.
