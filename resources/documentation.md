# Judge: Parallel Guardrail Evaluation Engine

## Executive Summary

**Judge** is a modular, real-time input evaluation engine designed for enforcing content safety guardrails on user prompts in LLM-based applications. By parsing policy logic into a binary evaluation tree and leveraging parallel evaluation through asyncio and small language models (SLMs), Judge ensures ultra-fast classification against customizable safety policies. It is scalable, extensible, and ideal for detecting NSFW content, jailbreak attempts, hate speech, and more.

---

## Table of Contents

- [Why Judge Exists](#why-judge-exists)
- [Core Concepts & Architecture](#core-concepts--architecture)
  - [Input Structure](#input-structure)
  - [Binary Evaluation Tree](#binary-evaluation-tree)
  - [Parallel Evaluation](#parallel-evaluation)
- [Key Modules Explained](#key-modules-explained)
- [Performance & Scalability](#performance--scalability)
- [Extending the System](#extending-the-system)
- [Usage Instructions](#usage-instructions)
- [Glossary](#glossary)

---

## Why Judge Exists

In modern LLM applications, ensuring safety, ethics, and contextual relevance of user input is non-negotiable. Sequentially checking prompts against multiple policies causes latency bottlenecks. **Judge** solves this by:

- Evaluating all policies concurrently
- Using lightweight, configurable evaluators (SLMs)
- Dynamically adapting to evolving misuse patterns via policy JSONs

It helps prevent:

- NSFW content
- Jailbreak/prompt injection
- Hate speech and discrimination
- Malicious use and social engineering
- Off-topic or irrelevant queries
---

## Core Concepts & Architecture

### Input Structure

Each evaluation takes 3 inputs:

1. **User Input** – raw text prompt.
2. **Logical Statement** – Boolean expression dictating how policy results combine.
3. **Policy Set** – A JSON file defining evaluation instructions for each policy.

Example statement:

```plaintext
(NSFW AND Jailbreak) AND (HateSpeech AND MaliciousExploitation) AND OffTopic
```

### Binary Evaluation Tree

The logical statement is parsed into a **binary tree**, where:

- **Leaf nodes** represent individual policy checks (e.g., NSFW)
- **Internal nodes** represent logical operators (AND, OR, NOT)

The tree is constructed via a custom Shunting-yard parser that respects logical precedence:

```plaintext
NOT > AND > OR
```

#### Binary Tree for `(PolicyA AND PolicyB) OR PolicyC]`


<p align="center">
  <img src="https://raw.githubusercontent.com/parzi-val/judge/main/resources/tree.png" width="360">
</p>




### Parallel Evaluation

Judge evaluates the binary tree **concurrently** using `asyncio`:

- Each internal node spawns parallel tasks for its children.
- Leaf nodes call `SLMWrapper(policy, user_input)` asynchronously.
- Final result is aggregated from children via logical ops.

**Performance benefit:**

```
Total Latency ≈ max(SLM call time), not sum
```

---
#### Architecture Diagram
![architecture diagram](https://raw.githubusercontent.com/parzi-val/judge/refs/heads/main/resources/arch.png)
---
## Key Modules Explained

### `core/engine.py`

- Represents a node in the binary tree (leaf or operator)
- Parses logical expressions into trees
- Evaluates them recursively and asynchronously
- Returns final compliance result and policy-wise result map

### `core/policy.py`

- Holds name, alias, and detailed evaluation instruction.
- Loads all policies from a JSON file.

### `core/slm_wrapper.py`

- Async wrapper for an SLM model (e.g., Google's Gemma)
- Sends formatted prompt using policy instruction
- Parses structured JSON output (`compliant`, `violation`, `highlighted_text`)
- Fallbacks to `"unknown"` on parse failure

### `core/prompt.py`

- Defines a master prompt template used across all policy evaluations.
- Template enforces strict JSON output formatting.

### `main.py`

- Initializes models and policies
- Defines the logical statement
- Manages the persistent asyncio event loop
- Defines `evaluate_prompt()` for prompt evaluation

### `app.py`

- Streamlit-based UI for testing Judge in real time

---

## Performance & Scalability

- **Async Parallelism**: All policy evaluations run concurrently
- **Balanced Binary Tree**: Ensures logical efficiency (O(log n) depth)
- **Reusable Event Loop**: Reduces overhead from recreating loops
- **Lightweight Evaluators**: SLMs are fast and low-cost

---

## Extending the System

### Adding New Policies

- Add to `policy.json` with `name`, `alias`, and `policy_instruction`
- Map the alias to an `SLMWrapper` in `main.py`

### Adding New Evaluator Types

- Implement a new wrapper class with `evaluate_policy(policy, user_input) -> (name, result)`
- Can be:
  - Rule-based
  - Regex-based
  - External API
  - Embedding-based classifiers

### Meta-Policies

- Judge supports content-routing and behavior-layer policies too (e.g., OffTopic).
---

## Usage Instructions

1. **Define your policies** in `policy.json`
2. **Write your logical statement** in `main.py`
3. **Set up environment**:

```bash
GOOGLE_API_KEY=your-key
```

4. **Run the app**:

```bash
streamlit run app.py
```

5. **Test prompts** and view real-time evaluations
---

## Glossary

| Term              | Description                                                         |
| ----------------- | ------------------------------------------------------------------- |
| Policy            | A rule defining compliance requirements for a specific category     |
| Policy Alias      | Short identifier used in logical statements                         |
| SLMWrapper        | Interface to evaluate prompts with a small language model           |
| EvaluationNode    | Node in binary tree (policy or logical operator)                    |
| result_map        | Dict mapping policy aliases to their evaluation results             |
| Logical Statement | Boolean expression combining multiple policies (e.g., A AND B OR C) |

---
For source code, see: [github.com/parzi-val/judge](https://github.com/parzi-val/judge)
