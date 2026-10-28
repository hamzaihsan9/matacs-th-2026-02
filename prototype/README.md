# Triage Engine Prototype

This prototype provides a functional implementation of the hybrid proposal triage pipeline designed in reference MATACS-TH-2026-02.

It demonstrates:
1. Dynamic Criteria Configuration: Evaluation rules, mandatory thresholds, and weights are defined as configuration objects, never hardcoded.
2. Adversarial Injection Detection: Document text is scanned for injection vectors and manipulation attempts prior to AI processing.
3. Grounding Verification: Verifies that extracted facts cite verbatim text substrings from the source document.
4. Deterministic Scoring: Executes mathematical formulas for price normalization, experience ratios, timeline duration, and warranty benchmarks.
5. Zero-Cost Re-Scoring: Shows how criteria weights can be modified dynamically and proposals re-evaluated in under one millisecond without re-extracting documents or calling LLM APIs.

---

## Directory Structure

```text
prototype/
├── .env.example         # Environment template for API keys
├── requirements.txt     # Python dependencies (pydantic, pytest)
├── models.py            # Pydantic data schemas for criteria, extraction, and audit events
├── security.py          # Rule-based adversarial and prompt injection scanner
├── config.py            # Dynamic category configuration (Commercial Solar Installation)
├── extractor.py         # Grounding-enforced proposal extraction module
├── engine.py            # Deterministic compliance and scoring engine
├── main.py              # CLI demonstration script
└── test_triage.py       # Comprehensive pytest suite
```

---

## Setup and Installation

### 1. Requirements
- Python 3.10+
- Virtual environment (recommended)

### 2. Install Dependencies
```bash
pip install -r prototype/requirements.txt
```

---

## Running the Prototype CLI

Execute the demonstration script from the repository root:

```bash
python3 prototype/main.py
```

The script runs the complete pipeline across Proposals A through E:
1. Summarizes extracted fields and flags.
2. Checks mandatory compliance (disqualifying Proposal B).
3. Catches prompt injection attempts (flagging Proposal C).
4. Computes itemized mathematical scores for eligible proposals (A, E, D).
5. Compares generated results against `ranking.json` for 100% parity.
6. Simulates an administrative weight change and demonstrates sub-millisecond re-scoring.

---

## Running the Test Suite

Run unit and integration tests using pytest:

```bash
pytest prototype/test_triage.py -v
```
