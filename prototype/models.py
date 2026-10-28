"""
Data models for the AI-Assisted Proposal Triage Engine.
Reference: MATACS-TH-2026-02
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ProposalStatus(str, Enum):
    RANKED = "ranked"
    FLAGGED = "flagged"
    INELIGIBLE = "ineligible"


class MandatoryCheckType(str, Enum):
    BOOLEAN_TRUE = "boolean_true"
    MIN_NUMBER = "min_number"
    MAX_NUMBER = "max_number"


class MandatoryCriterion(BaseModel):
    id: str
    name: str
    description: str
    check_type: MandatoryCheckType
    target_field: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class ScoringMetricType(str, Enum):
    BENCHMARK_RATIO = "benchmark_ratio"
    INVERSE_LINEAR = "inverse_linear"
    TIERED_SCALE = "tiered_scale"
    SUB_COMPONENTS = "sub_components"


class WeightedCriterion(BaseModel):
    id: str
    name: str
    description: str
    weight: float = Field(..., ge=0.0, le=100.0)
    metric_type: ScoringMetricType
    target_field: str
    benchmark_value: Optional[float] = None
    ceiling_value: Optional[float] = None
    sub_components: Optional[Dict[str, float]] = None


class CategoryCriteria(BaseModel):
    category_id: str
    name: str
    version: str
    project_scope: str
    budget_ceiling_cad: float
    max_timeline_weeks: int
    mandatory_criteria: List[MandatoryCriterion]
    weighted_criteria: List[WeightedCriterion]


class ExtractedField(BaseModel):
    value: Any
    quote: Optional[str] = None
    page: Optional[int] = None
    confidence: float = 1.0


class ExtractedProposal(BaseModel):
    proposal_id: str
    bidder_name: str
    ontario_licence_stated: ExtractedField
    licence_held_directly_by_bidder: ExtractedField
    licence_number: ExtractedField
    wsib_clearance_confirmed: ExtractedField
    liability_insurance_amount_cad: ExtractedField
    commercial_installs_100kw_plus: ExtractedField
    total_price_cad: ExtractedField
    completion_weeks: ExtractedField
    panel_warranty_years: ExtractedField
    workmanship_warranty_years: ExtractedField
    named_project_lead: ExtractedField
    certified_crew: ExtractedField
    site_safety_plan_included: ExtractedField
    performance_monitoring_months: ExtractedField
    suspicious_instructions: List[Dict[str, Any]] = Field(default_factory=list)


class ItemizedScore(BaseModel):
    criterion_id: str
    criterion_name: str
    weight: float
    raw_value: Any
    score: float
    max_score: float
    calculation_note: str


class ProposalEvaluationResult(BaseModel):
    proposal: str
    bidder_name: str
    rank: Optional[int] = None
    status: ProposalStatus
    score: Optional[float] = None
    reason: str
    itemized_scores: List[ItemizedScore] = Field(default_factory=list)
    failed_mandatory_criteria: List[str] = Field(default_factory=list)
    security_flags: List[str] = Field(default_factory=list)


class AuditEvent(BaseModel):
    event_id: str
    timestamp: str
    event_type: str
    proposal_id: str
    criteria_version: str
    status: str
    score: Optional[float]
    details: Dict[str, Any]
