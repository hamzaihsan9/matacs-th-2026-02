# Architectural Design Write-Up

Reference: MATACS-TH-2026-02

## 1. AI vs. Rules

The architecture strictly separates unstructured document comprehension from deterministic evaluation.

### AI-Powered Steps
Large Language Models are utilized solely for factual entity extraction:
- Extracting unstructured proposal text into typed JSON objects according to dynamic category schemas.
- Normalizing vendor phrasing (e.g., mapping team descriptions to structured crew counts and certifications).
- Extracting exact verbatim quotes with source page references for every attribute to ensure grounding.

### Rule-Based Steps
Plain code handles all validation, compliance, and scoring:
- Input sanitization and heuristic detection of prompt injection patterns.
- Mandatory compliance checks (pass/fail validation of licensing, WSIB clearance, insurance, and budget ceilings).
- Deterministic scoring calculations using weighted mathematical formulas (price normalization, experience ratios, warranty duration benchmarks).
- Ranking assignment and status classification (ranked, flagged, ineligible).
- Audit event logging, database persistence, and schema versioning.

### Boundary Rationale
LLMs are probabilistic and susceptible to manipulation and arithmetic hallucination. They must never directly assign scores or determine awards. Plain code guarantees 100% mathematical precision, complete auditability, and zero-cost score re-calculations.

---

## 2. Consistency and Explainability

### Repeatability
Deterministic repeatability is achieved by isolating extraction from scoring:
- Extraction runs at temperature 0.0 with strict JSON schema enforcement.
- Extracted JSON payloads are validated and permanently cached alongside their cryptographic content hashes.
- The scoring engine executes pure mathematical functions. Scoring the same proposal multiple times against identical criteria produces identical numeric scores and rankings down to the decimal point.

### Explainability
Reviewers never receive an opaque score:
- Mathematical Traceability: Each proposal displays an itemized breakdown of weighted sub-scores (e.g., Proposal A: Experience 30.0/30, Price 24.3/25, Timeline 15.0/15, Warranty 13.8/15, Team 15.0/15 = 98.0/100).
- Verbatim Grounding: Every extracted field links to a clickable citation and page number in the original PDF. A reviewer can click "ECRA/ESA #7001234" to highlight the exact text on Page 1.
- Explicit Exclusion Diagnoses: Non-ranked proposals display clear operational reasons (e.g., Proposal B notes mandatory disqualification due to unconfirmed subcontractor licensing; Proposal C notes security flagging due to prompt injection).

---

## 3. Human in the Loop and Audit Logging

The tool acts strictly as an advisory triage copilot. Final procurement decisions remain with human officers.

### Human Review Checkpoints
1. Intake Triage Gate: Reviewers inspect proposals classified as ineligible or flagged before proceeding. Proposal B can be confirmed for disqualification, and Proposal C can be escalated for security review.
2. Citation Verification: Reviewers inspect low-confidence extractions or flagged anomalies (such as Proposal D's uncommitted schedule) against highlighted PDF source pages.
3. Reviewer Overrides: Authorized reviewers can adjust any extracted fact or score component. An override requires selecting a reason code and providing a mandatory justification note.
4. Final Award Decision: The system produces a ranked recommendation; the designated facilities manager makes the final award decision and signs off.

### Immutable Audit Logging
All interactions are recorded in an append-only audit event log:
- Criteria Snapshot: Full record of category criteria, weights, and version IDs active at scoring time.
- Extraction Hashes: SHA-256 hashes of raw text, LLM prompts, model identifier, and raw LLM responses.
- Scoring Calculations: Explicit input parameters, intermediate formula outputs, and final scores.
- Reviewer Actions: User ID, timestamp, prior value, updated value, and mandatory reason for every override.

---

## 4. Changing Criteria and Weights

Procurement criteria evolve over administrative cycles. The system supports dynamic updates without hardcoding:

### Schema Versioning
Categories and criteria definitions are stored with immutable semantic versions (e.g., `solar_windsor_v1.0.0`). Each proposal evaluation records the exact criteria version ID used.

### Instant Zero-Cost Re-Scoring
Because factual extraction is decoupled from scoring, changing criteria never requires re-running LLM queries:
- Cached extracted facts (licensing, price, timeline, installations) remain valid.
- When an admin adjusts criteria weights (e.g., shifting price from 25% to 35%), the rule engine re-computes scores across all candidate proposals in milliseconds in memory.

### Lifecycle Management
The admin interface provides a Draft/Publish workflow:
- Admins can preview weight changes in a draft sandbox, inspecting projected score and rank shifts across existing submissions before committing.
- Publishing creates a new criteria version. The system prompts the administrator to re-score the existing batch or archive the prior evaluation run, recording the event in the audit trail.

---

## 5. Risks and Safeguards

| Risk | Consequence | Engineering Safeguard |
| :--- | :--- | :--- |
| Extraction Error / Hallucination | Inaccurate data fed into scoring engine. | Mandatory verbatim grounding. Extracted quotes are programmatically validated against source text (`quote in doc_text`). Unverified values trigger a human review flag. |
| Adversarial Prompt Injection | Vendor text attempts to override instructions (as seen in Proposal C). | Strict separation of system prompt and document text. Input text is sanitized and wrapped in passive delimiters. Regex filters detect injection patterns. Scoring rules are enforced entirely outside the LLM context. |
| Evaluation Bias | Unequal treatment based on formatting or brand. | Anonymized extraction mode strips bidder branding before LLM parsing. Proposals are evaluated independently against standardized rubrics rather than compared pairwise in model context. |
| Missing Information | Inability to evaluate a weighted metric (as seen in Proposal D). | Deterministic fallback: missing required attributes receive zero points in weighted calculations and generate a visible triage notice for human clarification. |
| Operating Cost and Latency | High LLM API overhead on large submissions. | LLM calls occur once per proposal during initial ingestion. Extracted JSON is cached. All subsequent triage, sorting, and weight re-evaluations run via sub-millisecond local code. |
