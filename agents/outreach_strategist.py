"""Turn a prospect profile into an actionable outreach strategy."""

from __future__ import annotations

import json
from typing import Any

from scoring.opportunity_scorer import OpportunityScorer
from services.llm_service import GeminiService


OUTREACH_SCHEMA = {
    "type": "object",
    "properties": {
        "recommended_approach": {
            "type": "string",
        },
        "value_proposition": {
            "type": "string",
        },
        "engagement_angles": {
            "type": "array",
            "items": {"type": "string"},
        },
        "talking_points": {
            "type": "array",
            "items": {"type": "string"},
        },
        "discovery_questions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "recommended_next_actions": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "recommended_approach",
        "value_proposition",
        "engagement_angles",
        "talking_points",
        "discovery_questions",
        "recommended_next_actions",
    ],
}


class OutreachStrategist:
    def __init__(
        self,
        llm: GeminiService,
    ) -> None:
        self.llm = llm

    @staticmethod
    def _rank_opportunities(
        profile: dict[str, Any],
    ) -> list[dict[str, Any]]:
        ranked_opportunities = []

        for opportunity in profile.get(
            "opportunities",
            [],
        ):
            score = OpportunityScorer.score(
                opportunity.get(
                    "signal_strength",
                    0,
                ),
                opportunity.get(
                    "pain_point_relevance",
                    0,
                ),
                opportunity.get(
                    "business_fit",
                    0,
                ),
                opportunity.get(
                    "recency",
                    0,
                ),
            )

            ranked_opportunities.append(
                {
                    **opportunity,
                    "opportunity_score": score,
                    "priority": (
                        OpportunityScorer.priority(score)
                    ),
                }
            )

        ranked_opportunities.sort(
            key=lambda item: item[
                "opportunity_score"
            ],
            reverse=True,
        )

        return ranked_opportunities

    def run(
        self,
        profile: dict[str, Any],
        offering: str,
    ) -> dict[str, Any]:
        """Generate an outreach plan without message copy."""

        ranked_opportunities = (
            self._rank_opportunities(profile)
        )

        if not ranked_opportunities:
            return {
                "ranked_opportunities": [],
                "strategy": None,
            }

        prompt = f"""
You are a B2B Outreach Strategist.

Explain how our business should approach the relevant
people for the evidence-backed opportunities below.

Our offering:

{offering}

Company profile:

{json.dumps(
    profile,
    ensure_ascii=False,
    indent=2,
)}

Ranked opportunities:

{json.dumps(
    ranked_opportunities,
    ensure_ascii=False,
    indent=2,
)}

Rules:

- Do not create an email.
- Do not create a LinkedIn message.
- Do not generate contact details.
- Use only people listed in people_to_reach.
- Never present inferred pain points as confirmed facts.
- Do not invent names, relationships, metrics or outcomes.
- Provide exactly 3 engagement angles.
- Provide exactly 3 talking points.
- Provide exactly 3 discovery questions.
- Provide exactly 3 recommended next actions.
"""

        strategy = self.llm.generate_json(
            prompt,
            OUTREACH_SCHEMA,
        )

        return {
            "ranked_opportunities": ranked_opportunities,
            "strategy": strategy,
        }