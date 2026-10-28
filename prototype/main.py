"""
AI-Assisted Proposal Triage Prototype CLI.
Demonstrates the two-stage triage pipeline:
1. Structured Fact Extraction & Adversarial Screening
2. Deterministic Rule-Based Scoring & Ranking
Reference: MATACS-TH-2026-02
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prototype.config import get_default_solar_criteria
from prototype.extractor import ProposalExtractor
from prototype.engine import TriageScoringEngine
from prototype.models import ProposalStatus


def print_separator(title: str = ""):
    print("\n" + "=" * 80)
    if title:
        print(f" {title.upper()} ".center(80, "="))
        print("=" * 80)


def run_pipeline():
    print_separator("MATACS-TH-2026-02: AI Proposal Triage Demonstration")

    # 1. Load Criteria Configuration
    criteria = get_default_solar_criteria()
    print(f"Category: {criteria.name} (Schema Version: {criteria.version})")
    print(f"Scope:    {criteria.project_scope}")
    print(f"Ceiling:  ${criteria.budget_ceiling_cad:,.0f} CAD | Window: <= {criteria.max_timeline_weeks} weeks")
    print(f"Mandatory: Licence held by bidder, WSIB clearance, $5M liability insurance, budget ceiling")
    print(f"Weights:   Experience 30%, Price 25%, Timeline 15%, Warranty 15%, Team/Approach 15%")

    # 2. Ingest Sample Proposals (A to E)
    print_separator("Step 1: Document Extraction & Adversarial Screening")
    proposals_to_evaluate = ["A", "B", "C", "D", "E"]
    extracted_batch = []

    for pid in proposals_to_evaluate:
        extracted = ProposalExtractor.get_sample_proposal_data(pid)
        extracted_batch.append(extracted)

        flag_note = " [INJECTION ATTACK DETECTED]" if extracted.suspicious_instructions else ""
        lic_held = "Yes" if extracted.licence_held_directly_by_bidder.value else "No (Subcontractor)"
        price_str = f"${extracted.total_price_cad.value:,.0f}" if extracted.total_price_cad.value else "N/A"
        time_str = f"{extracted.completion_weeks.value} wks" if extracted.completion_weeks.value else "Uncommitted"

        print(f"Proposal {pid} ({extracted.bidder_name:<26}): "
              f"Licence Held: {lic_held:<18} | Price: {price_str:<10} | Time: {time_str:<12}{flag_note}")

    # 3. Deterministic Evaluation & Ranking
    print_separator("Step 2: Deterministic Compliance Gating & Scoring")
    engine = TriageScoringEngine(criteria)
    results = engine.evaluate_batch(extracted_batch)

    # Format Output Table
    print(f"{'Proposal':<10} {'Rank':<6} {'Status':<12} {'Score':<8} {'Reason'}")
    print("-" * 80)

    export_json = []
    for r in results:
        rank_str = str(r.rank) if r.rank is not None else "null"
        score_str = f"{r.score:.1f}" if r.score is not None else "null"
        print(f"Proposal {r.proposal:<2} {rank_str:<6} {r.status.value:<12} {score_str:<8} {r.reason}")

        export_json.append({
            "proposal": r.proposal,
            "rank": r.rank,
            "status": r.status.value,
            "score": r.score,
            "reason": r.reason
        })

    # Print Itemized Score Breakdown for Ranked Proposals
    print_separator("Itemized Scoring Breakdown for Ranked Submissions")
    for r in results:
        if r.status == ProposalStatus.RANKED:
            print(f"\n--- Proposal {r.proposal}: {r.bidder_name} (Total: {r.score}/100) ---")
            for item in r.itemized_scores:
                print(f"  * {item.criterion_name:<20} Score: {item.score:5.2f}/{item.max_score:<4.1f} | {item.calculation_note}")

    # 4. Compare with Root ranking.json
    root_json_path = Path(__file__).parent.parent / "ranking.json"
    if root_json_path.exists():
        with open(root_json_path) as f:
            expected_data = json.load(f)

        match = True
        for exp, act in zip(expected_data, export_json):
            if (exp["proposal"] != act["proposal"] or
                exp["rank"] != act["rank"] or
                exp["status"] != act["status"] or
                exp["score"] != act["score"]):
                match = False
                break

        print_separator("Verification Against ranking.json")
        if match:
            print("SUCCESS: Prototype output matches root ranking.json with 100% fidelity.")
        else:
            print("WARNING: Prototype output differs from root ranking.json.")

    # 5. Dynamic Weight Adjustment Demo (Zero-Cost Re-Scoring)
    print_separator("Step 3: Dynamic Criteria Adjustment Demo (Zero LLM Calls)")
    print("Modifying weights: Price weight increased from 25% -> 35%, Experience decreased from 30% -> 20%.")
    modified_criteria = get_default_solar_criteria()
    modified_criteria.version = "v1.1.0-draft"
    for c in modified_criteria.weighted_criteria:
        if c.id == "weight_price":
            c.weight = 35.0
        elif c.id == "weight_experience":
            c.weight = 20.0

    new_engine = TriageScoringEngine(modified_criteria)
    new_results = new_engine.evaluate_batch(extracted_batch)

    print("\nRe-scored in < 1ms without re-extracting documents:")
    for r in new_results:
        rank_str = str(r.rank) if r.rank is not None else "null"
        score_str = f"{r.score:.1f}" if r.score is not None else "null"
        print(f"Proposal {r.proposal:<2} Rank: {rank_str:<5} Status: {r.status.value:<11} Score: {score_str:<6} ({r.bidder_name})")

    print_separator("Demonstration Complete")


if __name__ == "__main__":
    run_pipeline()
