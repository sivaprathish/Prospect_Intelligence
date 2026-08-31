"""Create an evidence-backed company and people prospect profile."""

from __future__ import annotations

import json
from typing import Any

from services.firecrawl_service import FirecrawlService
from services.llm_service import GeminiService
from services.seltz_service import SeltzService


PROFILE_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {"type": "string"},
        "domain": {"type": "string"},
        "company_summary": {"type": "string"},
        "industry": {"type": "string"},
        "products_services": {
            "type": "array",
            "items": {"type": "string"},
        },
        "target_customers": {
            "type": "array",
            "items": {"type": "string"},
        },
        "competitors": {
            "type": "array",
            "items": {"type": "string"},
        },
        "industry_trends": {
            "type": "array",
            "items": {"type": "string"},
        },
        "signals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "signal_type": {"type": "string"},
                    "summary": {"type": "string"},
                    "event_date": {
                        "type": ["string", "null"]
                    },
                    "business_impact": {
                        "type": "string"
                    },
                    "signal_strength": {
                        "type": "number"
                    },
                    "recency_score": {
                        "type": "number"
                    },
                    "source_url": {
                        "type": "string"
                    },
                },
                "required": [
                    "signal_type",
                    "summary",
                    "business_impact",
                    "signal_strength",
                    "recency_score",
                    "source_url",
                ],
            },
        },
        "pain_points": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string"
                    },
                    "status": {
                        "type": "string",
                        "enum": [
                            "confirmed",
                            "inferred",
                        ],
                    },
                    "source_url": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                },
                "required": [
                    "description",
                    "status",
                ],
            },
        },
        "challenges": {
            "type": "array",
            "items": {"type": "string"},
        },
        "opportunities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    },
                    "matched_pain_point": {
                        "type": "string"
                    },
                    "signal_strength": {
                        "type": "number"
                    },
                    "pain_point_relevance": {
                        "type": "number"
                    },
                    "business_fit": {
                        "type": "number"
                    },
                    "recency": {
                        "type": "number"
                    },
                },
                "required": [
                    "title",
                    "description",
                    "matched_pain_point",
                    "signal_strength",
                    "pain_point_relevance",
                    "business_fit",
                    "recency",
                ],
            },
        },
        "source_urls": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "company_name",
        "domain",
        "company_summary",
        "industry",
        "products_services",
        "target_customers",
        "competitors",
        "industry_trends",
        "signals",
        "pain_points",
        "challenges",
        "opportunities",
        "source_urls",
    ],
}


PEOPLE_SCHEMA = {
    "type": "object",
    "properties": {
        "people_to_reach": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "current_title": {
                        "type": "string"
                    },
                    "company": {
                        "type": "string"
                    },
                    "department": {
                        "type": "string"
                    },
                    "seniority": {
                        "type": "string"
                    },
                    "profile_url": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                    "matched_opportunity": {
                        "type": "string"
                    },
                    "why_relevant": {
                        "type": "string"
                    },
                    "conversation_topic": {
                        "type": "string"
                    },
                    "contact_fit_score": {
                        "type": "number"
                    },
                    "employment_status": {
                        "type": "string",
                        "enum": [
                            "confirmed_current",
                            "likely_current",
                        ],
                    },
                    "source_urls": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                    },
                },
                "required": [
                    "name",
                    "current_title",
                    "company",
                    "department",
                    "seniority",
                    "profile_url",
                    "matched_opportunity",
                    "why_relevant",
                    "conversation_topic",
                    "contact_fit_score",
                    "employment_status",
                    "source_urls",
                ],
            },
        },
    },
    "required": ["people_to_reach"],
}


class ProspectIntelligenceAgent:
    def __init__(
        self,
        firecrawl: FirecrawlService,
        seltz: SeltzService,
        llm: GeminiService,
    ) -> None:
        self.firecrawl = firecrawl
        self.seltz = seltz
        self.llm = llm

    def run(
        self,
        company_name: str,
        company_domain: str,
        offering: str,
    ) -> dict[str, Any]:
        """Build the complete prospect profile."""

        if not company_name.strip():
            raise ValueError("Company name is required")

        if not company_domain.strip():
            raise ValueError("Company domain is required")

        if not offering.strip():
            raise ValueError("Offering is required")

        official_sources = self.firecrawl.research_company(
            company_name,
            company_domain,
        )

        market_sources = self.seltz.research_market(
            company_name,
            company_domain,
        )

        company_evidence = (
            official_sources + market_sources
        )

        if not company_evidence:
            return {
                "company_name": company_name,
                "domain": company_domain,
                "company_summary": "",
                "industry": "",
                "products_services": [],
                "target_customers": [],
                "competitors": [],
                "industry_trends": [],
                "signals": [],
                "pain_points": [],
                "challenges": [],
                "opportunities": [],
                "people_to_reach": [],
                "source_urls": [],
                "research_summary": {
                    "firecrawl_sources": 0,
                    "seltz_sources": 0,
                    "people_sources": 0,
                    "total_sources": 0,
                },
            }

        profile_prompt = f"""
You are a B2B Prospect Intelligence Agent.

Build a balanced and evidence-backed company prospect
profile using the supplied official and external sources.

Target company: {company_name}
Official domain: {company_domain}
Our offering: {offering}

Rules:

- Use only the supplied evidence.
- Preserve relevant source URLs.
- Separate confirmed pain points from inferred pain points.
- Do not invent revenue, employee count, customers,
  competitors, events or dates.
- Identify recent business signals such as funding,
  expansion, partnerships, product launches, acquisitions,
  leadership changes, hiring, regulation, transformation
  and major contracts.
- Every opportunity must connect the offering to a signal,
  pain point, challenge or industry trend.
- Score all opportunity components from 0 to 100.
- Return a maximum of 5 signals.
- Return a maximum of 5 opportunities.
- Put the strongest signals and opportunities first.

Evidence:

{json.dumps(
    company_evidence,
    ensure_ascii=False,
)[:100000]}
"""

        profile = self.llm.generate_json(
            profile_prompt,
            PROFILE_SCHEMA,
        )

        opportunity_titles = [
            opportunity.get("title", "")
            for opportunity in profile.get(
                "opportunities",
                [],
            )
            if opportunity.get("title")
        ]

        people_evidence = self.seltz.search_people(
            company_name=company_name,
            company_domain=company_domain,
            opportunity_titles=opportunity_titles,
            max_results=15,
        )

        people_to_reach: list[dict[str, Any]] = []

        if people_evidence:
            people_prompt = f"""
You are a B2B decision-maker research analyst.

Identify the most relevant current employees to approach
for the supplied business opportunities.

Company: {company_name}
Official domain: {company_domain}

Business opportunities:

{json.dumps(
    profile.get("opportunities", []),
    ensure_ascii=False,
    indent=2,
)}

Public professional evidence:

{json.dumps(
    people_evidence,
    ensure_ascii=False,
    indent=2,
)[:60000]}

Rules:

- Return a maximum of 5 people.
- Rank people by contact fit.
- Include only people currently working at the exact
  target company.
- Exclude former employees.
- Exclude advisors and advisory board members.
- Exclude investors, consultants and unrelated people.
- Evidence must support the person's name, title and
  current employer.
- Do not invent names, titles, employment or profile URLs.
- Do not create email addresses or phone numbers.
- Use null when a profile URL is unavailable.
- Match each person to one supplied opportunity.
- Explain why the person is relevant.
- Suggest an evidence-based conversation topic.
- Score contact fit from 0 to 100.
"""

            people_result = self.llm.generate_json(
                people_prompt,
                PEOPLE_SCHEMA,
            )

            people_to_reach = people_result.get(
                "people_to_reach",
                [],
            )

            people_to_reach.sort(
                key=lambda person: person.get(
                    "contact_fit_score",
                    0,
                ),
                reverse=True,
            )

        profile["people_to_reach"] = people_to_reach

        profile["research_summary"] = {
            "firecrawl_sources": len(official_sources),
            "seltz_sources": len(market_sources),
            "people_sources": len(people_evidence),
            "total_sources": (
                len(company_evidence)
                + len(people_evidence)
            ),
        }

        return profile