"""Echomind Commerce - agent swarm (OpenRouter + Gemini direct).

Modules planned (per WINNING_PLAN §5.2 / §15):
    base.py           - AgentClient ABC
    openrouter.py     - OpenRouter client (one path for all 4 free-tier models)
    gemini_agent.py   - direct Gemini agent simulator
    prompt_gen.py     - buyer-intent prompt generator
    runner.py         - concurrency + retries + persistence
    adversarial.py    - "frustrated buyer" mode (§19.7)
"""
