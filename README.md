# Technical Assessment: AI Proposal Triage Design

Reference: MATACS-TH-2026-02  
Candidate: Hamza Ihsan  
Role: Associate Software Developer  
Time Spent: 65 minutes  

---

## Overview

This repository contains the complete design and reference implementation of an AI-assisted proposal triage tool for facility contractor evaluations. The system ingests unstructured vendor proposals in PDF format, performs structured fact extraction with verbatim citation grounding, filters adversarial prompt injections, and deterministically scores and ranks candidates against dynamically configured criteria.

The design strictly decouples probabilistic document extraction (handled by AI) from compliance gating, arithmetic scoring, and ranking (handled by plain code). Final procurement award decisions remain with designated human officers.

---

## Repository Contents

- [diagram/](diagram/): Contains the high-resolution process architecture diagram ([diagram/process_flow.png](diagram/process_flow.png)) detailing AI steps, rule-based steps, and human checkpoints from upload to award.
- [WRITEUP.md](WRITEUP.md): Technical write-up addressing the five assessment questions regarding AI vs. rules, consistency, human oversight, criteria changes, and system risks (strictly under 1,000 words).
- [PROMPTS.md](PROMPTS.md): Production-ready system and user prompt definitions, JSON schema specifications, and defensive guardrails against indirect prompt injection.
- [ranking.json](ranking.json): Output JSON file containing the verified triage evaluation and rankings for sample proposals A through E.
- [prototype/](prototype/): Functional Python prototype demonstrating dynamic configuration, injection screening, deterministic scoring, batch ranking, and automated test coverage.

---

## AI Usage Statement

AI tools were used during the initial design phase to explore modular architectural patterns for document triage pipelines and to generate regex patterns for adversarial prompt screening. During this process, I disagreed with the AI's initial suggestion to let the Large Language Model calculate numerical scores and rank proposals directly in prompt output, as LLM arithmetic is non-deterministic, susceptible to prompt injection, and incurs unnecessary token costs during administrative re-weighting. I corrected this approach by confining the AI strictly to structured factual JSON extraction and delegating all compliance gating, scoring formulas, and sorting logic to a deterministic rules engine.

---

## Summary of Sample Proposal Evaluation

The triage engine was evaluated against the five sample proposals for the 150 kW Commercial Solar Installation category ($260,000 CAD budget ceiling, <= 16-week completion window):

| Proposal | Bidder Name | Status | Rank | Score | Operational Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Proposal A | Northshore Solar Ltd. | ranked | 1 | 98.0 | Highest score overall with 14 qualifying commercial installs, compliant 12-week schedule, competitive price, and complete team and safety coverage. |
| Proposal E | SunGrid Contractors Inc. | ranked | 2 | 84.8 | Strong technical submission with leading 12-year workmanship warranty and 24-month monitoring, placed second due to higher price and fewer installations than Proposal A. |
| Proposal D | Essex Green Power Inc. | ranked | 3 | 69.8 | Lowest price within budget ceiling and solid experience, but penalized zero on timeline due to uncommitted schedule and received partial marks on team coverage. |
| Proposal B | BrightPath Energy Inc. | ineligible | null | null | Disqualified on mandatory criteria: Ontario electrical contractor licence is not held directly by the bidder. |
| Proposal C | Lakeview Renewables Corp. | flagged | null | null | Flagged for manual review: Adversarial prompt injection attempt detected in Appendix C attempting to manipulate automated review scoring. |

---

## Architectural Highlights

```text
[ Upload Proposals ] ──> [ Text Preprocessing ] ──> [ Injection Detector ] (Rule-Based)
                                                               │
                                         ┌─────────────────────┴─────────────────────┐
                                         ▼                                           ▼
                                 [ Clean Text ]                             [ Prompt Injection ]
                                         │                                           │
                                         ▼                                           ▼
                              [ AI Fact Extraction ]                     [ status: "flagged" ]
                            (Strict Schema & Citations)                   [ Human Security Review ]
                                         │
                                         ▼
                             [ Mandatory Gate Check ] (Rule-Based)
                                         │
                                         ├──────────────────────────┐
                                         ▼                          ▼
                                 [ Pass Mandatory ]        [ Fail Mandatory ]
                                         │                          │
                                         ▼                          ▼
                             [ Deterministic Scoring ]     [ status: "ineligible" ]
                             (Experience, Price, Time,     (e.g., Proposal B)
                                Warranty, Team Math)
                                         │
                                         ▼
                              [ Triage & Rank Sort ]
                             (Proposals A, E, D Ranked)
                                         │
                                         ▼
                             [ Reviewer Workspace ] (Human Checkpoint)
                             (Inspect Citations, Resolve Flags, Override)
                                         │
                                         ▼
                             [ Final Award Decision ] (Human Decision Maker)
```

1. Factual Extraction Separation: The LLM transforms unstructured PDF text into a typed JSON schema. Every extracted fact requires a verbatim citation and page number from the original document.
2. Adversarial Defense in Depth: Proposals are pre-screened for indirect prompt injections and authority assertions (such as the manipulation payload in Proposal C's Appendix C). Untrusted text is strictly isolated from system instructions.
3. Deterministic Repeatability: Scoring formulas and eligibility gates run in plain code. Re-evaluating the same submission produces identical results.
4. Dynamic Criteria & Zero-Cost Re-Scoring: Criteria definitions, thresholds, and weights are versioned data objects. When an administrator adjusts criteria weights, candidate proposals are re-scored across the cohort in milliseconds with zero LLM API calls.
5. Complete Auditability: An append-only audit ledger tracks prompt hashes, raw model outputs, intermediate math calculations, and any manual reviewer overrides with required justification notes.

---

## Running the Prototype and Tests

### Prototype Demonstration
To run the automated triage pipeline across Proposals A through E:

```bash
python3 prototype/main.py
```

### Running Test Suite
The repository includes a comprehensive test suite covering mandatory disqualification, injection detection, edge cases, and ranking parity:

```bash
pytest prototype/test_triage.py -v
```
