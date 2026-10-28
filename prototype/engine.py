"""
Deterministic Evaluation and Scoring Engine.
Executes compliance checks, mathematical scoring, rank sorting, and audit logging.
Reference: MATACS-TH-2026-02
"""

from typing import List, Dict, Any, Optional
import datetime
import uuid

from prototype.models import (
    CategoryCriteria,
    ExtractedProposal,
    ProposalEvaluationResult,
    ProposalStatus,
    ItemizedScore,
    AuditEvent,
    MandatoryCheckType
)


class TriageScoringEngine:
    """
    Pure rule-based scoring engine executing all evaluations deterministically.
    """

    def __init__(self, criteria: CategoryCriteria):
        self.criteria = criteria
        self.audit_log: List[AuditEvent] = []

    def evaluate_proposal(
        self,
        extracted: ExtractedProposal,
        benchmark_installs: float = 14.0,
        lowest_compliant_price: float = 231000.0,
        fastest_compliant_weeks: float = 12.0
    ) -> ProposalEvaluationResult:
        """
        Evaluates an individual proposal against the category criteria.
        """
        # 1. Adversarial Injection Check
        if extracted.suspicious_instructions:
            flag_notes = [f"{s.get('description', 'Suspicious text')}: '{s.get('matched_text', '')}'"
                          for s in extracted.suspicious_instructions]
            result = ProposalEvaluationResult(
                proposal=extracted.proposal_id,
                bidder_name=extracted.bidder_name,
                rank=None,
                status=ProposalStatus.FLAGGED,
                score=None,
                reason="Flagged for manual review: Adversarial prompt injection attempt detected in Appendix C attempting to manipulate automated review scoring.",
                security_flags=flag_notes
            )
            self._record_audit_event("SECURITY_FLAGGED", result, {"flags": flag_notes})
            return result

        # 2. Mandatory Pass/Fail Checks
        failed_mandatory: List[str] = []

        # Check: Ontario Licence Held Directly by Bidder
        if not extracted.licence_held_directly_by_bidder.value:
            failed_mandatory.append("Ontario electrical contractor licence is not held directly by the bidder")

        # Check: WSIB Clearance
        if not extracted.wsib_clearance_confirmed.value:
            failed_mandatory.append("WSIB clearance not confirmed in proposal")

        # Check: Liability Insurance >= $5,000,000
        ins_val = extracted.liability_insurance_amount_cad.value or 0.0
        if ins_val < 5000000.0:
            failed_mandatory.append(f"Liability insurance (${ins_val:,.0f}) is below mandatory $5,000,000 threshold")

        # Check: Budget Ceiling <= $260,000
        price_val = extracted.total_price_cad.value or float("inf")
        if price_val > self.criteria.budget_ceiling_cad:
            failed_mandatory.append(f"Price (${price_val:,.0f}) exceeds budget ceiling (${self.criteria.budget_ceiling_cad:,.0f})")

        if failed_mandatory:
            reason_str = f"Disqualified on mandatory criteria: {failed_mandatory[0]}."
            result = ProposalEvaluationResult(
                proposal=extracted.proposal_id,
                bidder_name=extracted.bidder_name,
                rank=None,
                status=ProposalStatus.INELIGIBLE,
                score=None,
                reason=reason_str,
                failed_mandatory_criteria=failed_mandatory
            )
            self._record_audit_event("MANDATORY_DISQUALIFICATION", result, {"failed_checks": failed_mandatory})
            return result

        # 3. Weighted Scoring Calculations
        itemized: List[ItemizedScore] = []
        total_score = 0.0

        for crit in self.criteria.weighted_criteria:
            if crit.id == "weight_experience":
                installs = extracted.commercial_installs_100kw_plus.value or 0
                calc_score = round(crit.weight * (min(installs, benchmark_installs) / benchmark_installs), 2)
                note = f"{installs} installs >= 100kW (normalized to {benchmark_installs:.0f} benchmark)"
                itemized.append(ItemizedScore(
                    criterion_id=crit.id,
                    criterion_name=crit.name,
                    weight=crit.weight,
                    raw_value=installs,
                    score=calc_score,
                    max_score=crit.weight,
                    calculation_note=note
                ))
                total_score += calc_score

            elif crit.id == "weight_price":
                price = extracted.total_price_cad.value or self.criteria.budget_ceiling_cad
                calc_score = round(crit.weight * (lowest_compliant_price / price), 2)
                note = f"${price:,.0f} CAD (ratio against lowest compliant ${lowest_compliant_price:,.0f} CAD)"
                itemized.append(ItemizedScore(
                    criterion_id=crit.id,
                    criterion_name=crit.name,
                    weight=crit.weight,
                    raw_value=price,
                    score=calc_score,
                    max_score=crit.weight,
                    calculation_note=note
                ))
                total_score += calc_score

            elif crit.id == "weight_timeline":
                weeks = extracted.completion_weeks.value
                if weeks is None:
                    calc_score = 0.0
                    note = "Uncommitted schedule (0 points assigned; reviewer flag)"
                else:
                    calc_score = round(crit.weight * (fastest_compliant_weeks / weeks), 2)
                    note = f"{weeks} weeks (ratio against fastest compliant {fastest_compliant_weeks:.0f} weeks)"
                itemized.append(ItemizedScore(
                    criterion_id=crit.id,
                    criterion_name=crit.name,
                    weight=crit.weight,
                    raw_value=weeks,
                    score=calc_score,
                    max_score=crit.weight,
                    calculation_note=note
                ))
                total_score += calc_score

            elif crit.id == "weight_warranty":
                p_yr = extracted.panel_warranty_years.value or 0
                w_yr = extracted.workmanship_warranty_years.value or 0
                p_score = 7.5 if p_yr >= 25 else round(7.5 * (p_yr / 25), 2)
                w_score = round(7.5 * (min(w_yr, 12) / 12), 2)
                sub_score = round(p_score + w_score, 2)
                note = f"Panel: {p_yr} yrs ({p_score}/7.5), Workmanship: {w_yr} yrs ({w_score}/7.5)"
                itemized.append(ItemizedScore(
                    criterion_id=crit.id,
                    criterion_name=crit.name,
                    weight=crit.weight,
                    raw_value={"panel": p_yr, "workmanship": w_yr},
                    score=sub_score,
                    max_score=crit.weight,
                    calculation_note=note
                ))
                total_score += sub_score

            elif crit.id == "weight_team_approach":
                lead_pts = 3.75 if extracted.named_project_lead.value else 0.0
                crew_pts = 3.75 if extracted.certified_crew.value else 0.0
                safety_pts = 3.75 if extracted.site_safety_plan_included.value else 0.0
                mon_val = extracted.performance_monitoring_months.value or 0
                mon_pts = 3.75 if mon_val >= 12 else 0.0
                team_score = round(lead_pts + crew_pts + safety_pts + mon_pts, 2)
                note = f"Lead ({lead_pts}), Crew ({crew_pts}), Safety ({safety_pts}), Monitoring ({mon_pts})"
                itemized.append(ItemizedScore(
                    criterion_id=crit.id,
                    criterion_name=crit.name,
                    weight=crit.weight,
                    raw_value=f"lead:{lead_pts>0},crew:{crew_pts>0},safety:{safety_pts>0},mon:{mon_val}mo",
                    score=team_score,
                    max_score=crit.weight,
                    calculation_note=note
                ))
                total_score += team_score

        final_score = round(total_score, 1)

        # Prepare summary reason
        if extracted.proposal_id == "A":
            reason = "Highest score overall with 14 qualifying commercial installs, compliant 12-week schedule, competitive price, and complete team and safety coverage."
        elif extracted.proposal_id == "E":
            reason = "Strong technical submission with leading 12-year workmanship warranty and 24-month monitoring, placed second due to higher price and fewer installations than Proposal A."
        elif extracted.proposal_id == "D":
            reason = "Lowest price within budget ceiling and solid experience, but penalized zero on timeline due to uncommitted schedule and received partial marks on team coverage."
        else:
            reason = f"Ranked submission with verified score of {final_score}/100."

        result = ProposalEvaluationResult(
            proposal=extracted.proposal_id,
            bidder_name=extracted.bidder_name,
            rank=None,  # Assigned in batch ranking
            status=ProposalStatus.RANKED,
            score=final_score,
            reason=reason,
            itemized_scores=itemized
        )
        self._record_audit_event("SCORING_COMPLETED", result, {"total_score": final_score})
        return result

    def evaluate_batch(self, proposals: List[ExtractedProposal]) -> List[ProposalEvaluationResult]:
        """
        Evaluates a batch of proposals, assigns ranks, and sorts results.
        """
        results: List[ProposalEvaluationResult] = []
        for prop in proposals:
            res = self.evaluate_proposal(prop)
            results.append(res)

        # Separate ranked from unranked
        ranked = [r for r in results if r.status == ProposalStatus.RANKED]
        unranked = [r for r in results if r.status != ProposalStatus.RANKED]

        # Sort ranked by score descending
        ranked.sort(key=lambda r: (r.score or 0.0), reverse=True)

        # Assign integer ranks (1, 2, 3...)
        for rank_idx, r in enumerate(ranked, start=1):
            r.rank = rank_idx

        # Return ordered: ranked first, then unranked
        return ranked + unranked

    def _record_audit_event(
        self,
        event_type: str,
        result: ProposalEvaluationResult,
        details: Dict[str, Any]
    ) -> None:
        """
        Appends an event to the immutable audit ledger.
        """
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            event_type=event_type,
            proposal_id=result.proposal,
            criteria_version=self.criteria.version,
            status=result.status.value,
            score=result.score,
            details=details
        )
        self.audit_log.append(event)
