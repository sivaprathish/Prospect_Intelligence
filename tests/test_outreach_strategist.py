from unittest.mock import MagicMock

from agents.outreach_strategist import OutreachStrategist


def test_ranks_opportunities_and_generates_strategy():
    llm = MagicMock()
    llm.generate_json.return_value = {
        "recommended_approach": "Lead with efficiency", "value_proposition": "Reduce manual work",
        "email_subject": "Scaling operations", "email_message": "Hello", "linkedin_message": "Hello",
        "discovery_questions": ["Q1", "Q2", "Q3"], "recommended_next_action": "Book a call",
    }
    profile = {"opportunities": [
        {"title": "Low", "description": "", "matched_pain_point": "", "signal_strength": 50, "pain_point_relevance": 50, "business_fit": 50, "recency": 50},
        {"title": "High", "description": "", "matched_pain_point": "", "signal_strength": 95, "pain_point_relevance": 90, "business_fit": 90, "recency": 100},
    ]}
    result = OutreachStrategist(llm).run(profile, "Automation")
    assert result["ranked_opportunities"][0]["title"] == "High"
    assert result["strategy"]["email_subject"] == "Scaling operations"


def test_no_opportunities_skips_llm():
    llm = MagicMock()
    result = OutreachStrategist(llm).run({"opportunities": []}, "Offering")
    assert result == {"ranked_opportunities": [], "strategy": None}
    llm.generate_json.assert_not_called()
