"""Echomind Commerce - five-phase Socratic interview engine.

Modules planned (per WINNING_PLAN §5.2 / §8):
    engine.py                - main interview loop
    question_gen.py          - Gemini Flash next-question generator
    extractor.py             - Gemini Flash typed extraction
    phase_manager.py         - 5-phase advancement triggers
    gap_analyzer.py          - interview gap detection (graph completeness)
    frontier_scorer.py       - what to ask next
    redundancy_checker.py    - semantic-equivalence dedup
    decision_tree_builder.py - narrative -> if-then JSON
"""
