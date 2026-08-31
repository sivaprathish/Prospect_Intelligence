from unittest.mock import MagicMock

import pytest

from agents.prospect_intelligence import ProspectIntelligenceAgent


def test_builds_profile_from_both_sources():
    firecrawl, seltz, llm = MagicMock(), MagicMock(), MagicMock()
    firecrawl.research_company.return_value = [{"url": "https://example.com/about", "content": "Official"}]
    seltz.research_market.return_value = [{"url": "https://news.example.com/a", "content": "External"}]
    llm.generate_json.return_value = {
        "company_name": "Example", "domain": "example.com", "company_summary": "Summary",
        "industry": "Technology", "products_services": [], "target_customers": [],
        "competitors": [], "industry_trends": [], "signals": [], "pain_points": [],
        "challenges": [], "opportunities": [], "source_urls": ["https://example.com/about"],
    }
    result = ProspectIntelligenceAgent(firecrawl, seltz, llm).run("Example", "example.com", "Automation")
    assert result["research_summary"] == {"firecrawl_sources": 1, "seltz_sources": 1, "total_sources": 2}
    firecrawl.research_company.assert_called_once_with("Example", "example.com")
    seltz.research_market.assert_called_once_with("Example", "example.com")


def test_requires_name_and_domain():
    agent = ProspectIntelligenceAgent(MagicMock(), MagicMock(), MagicMock())
    with pytest.raises(ValueError):
        agent.run("", "", "Offering")


def test_empty_evidence_returns_empty_profile():
    firecrawl, seltz = MagicMock(), MagicMock()
    firecrawl.research_company.return_value = []
    seltz.research_market.return_value = []
    result = ProspectIntelligenceAgent(firecrawl, seltz, MagicMock()).run("Example", "example.com", "Offering")
    assert result["opportunities"] == []
