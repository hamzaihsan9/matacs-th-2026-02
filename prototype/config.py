"""
Dynamic Category Configuration.
Criteria and weights are defined as configuration data, never hardcoded in the engine.
Reference: MATACS-TH-2026-02
"""

from prototype.models import (
    CategoryCriteria,
    MandatoryCriterion,
    WeightedCriterion,
    MandatoryCheckType,
    ScoringMetricType
)


def get_default_solar_criteria() -> CategoryCriteria:
    """
    Returns the dynamic criteria configuration for the Commercial Solar Installation category.
    """
    return CategoryCriteria(
        category_id="solar_windsor_warehouse",
        name="Commercial Solar Installation",
        version="v1.0.0",
        project_scope="150 kW rooftop system on warehouse in Windsor, Ontario",
        budget_ceiling_cad=260000.0,
        max_timeline_weeks=16,
        mandatory_criteria=[
            MandatoryCriterion(
                id="mand_licence_held",
                name="Ontario Electrical Contractor Licence",
                description="Licence held directly by the bidder and stated in the proposal",
                check_type=MandatoryCheckType.BOOLEAN_TRUE,
                target_field="licence_held_directly_by_bidder"
            ),
            MandatoryCriterion(
                id="mand_wsib",
                name="WSIB Clearance",
                description="Current WSIB clearance confirmed in proposal",
                check_type=MandatoryCheckType.BOOLEAN_TRUE,
                target_field="wsib_clearance_confirmed"
            ),
            MandatoryCriterion(
                id="mand_insurance",
                name="Liability Insurance Coverage",
                description="Commercial general liability insurance confirmed at or above $5,000,000 CAD",
                check_type=MandatoryCheckType.MIN_NUMBER,
                target_field="liability_insurance_amount_cad",
                min_value=5000000.0
            ),
            MandatoryCriterion(
                id="mand_budget_ceiling",
                name="Budget Ceiling Compliance",
                description="Total price must not exceed the project budget ceiling of $260,000 CAD",
                check_type=MandatoryCheckType.MAX_NUMBER,
                target_field="total_price_cad",
                max_value=260000.0
            )
        ],
        weighted_criteria=[
            WeightedCriterion(
                id="weight_experience",
                name="Relevant Experience",
                description="Commercial installs of 100 kW or more in the last 5 years",
                weight=30.0,
                metric_type=ScoringMetricType.BENCHMARK_RATIO,
                target_field="commercial_installs_100kw_plus",
                benchmark_value=14.0  # Normalized against benchmark
            ),
            WeightedCriterion(
                id="weight_price",
                name="Price",
                description="Lower total cost within the budget ceiling",
                weight=25.0,
                metric_type=ScoringMetricType.INVERSE_LINEAR,
                target_field="total_price_cad",
                ceiling_value=260000.0
            ),
            WeightedCriterion(
                id="weight_timeline",
                name="Timeline",
                description="Shorter completion time within 16 weeks",
                weight=15.0,
                metric_type=ScoringMetricType.INVERSE_LINEAR,
                target_field="completion_weeks",
                ceiling_value=16.0
            ),
            WeightedCriterion(
                id="weight_warranty",
                name="Warranty Coverage",
                description="Length of panel and workmanship warranties",
                weight=15.0,
                metric_type=ScoringMetricType.SUB_COMPONENTS,
                target_field="warranties",
                sub_components={
                    "panel_warranty_years": 7.5,
                    "workmanship_warranty_years": 7.5
                }
            ),
            WeightedCriterion(
                id="weight_team_approach",
                name="Team and Approach",
                description="Named project lead, crew, safety and monitoring plan",
                weight=15.0,
                metric_type=ScoringMetricType.SUB_COMPONENTS,
                target_field="team_and_approach",
                sub_components={
                    "named_project_lead": 3.75,
                    "certified_crew": 3.75,
                    "site_safety_plan_included": 3.75,
                    "performance_monitoring_months": 3.75
                }
            )
        ]
    )
