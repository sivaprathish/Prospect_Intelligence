"""End-to-end prospect intelligence workflow."""

from __future__ import annotations

from typing import Any

from agents.outreach_strategist import OutreachStrategist
from agents.prospect_intelligence import ProspectIntelligenceAgent


class ProspectWorkflow:
    def __init__(self, intelligence: ProspectIntelligenceAgent, outreach: OutreachStrategist) -> None:
        self.intelligence = intelligence
        self.outreach = outreach

    def run(self, company_name: str, company_domain: str, offering: str) -> dict[str, Any]:
        profile = self.intelligence.run(company_name, company_domain, offering)
        outreach = self.outreach.run(profile, offering)
        return {"profile": profile, **outreach}
