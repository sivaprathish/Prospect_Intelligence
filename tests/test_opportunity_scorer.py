import pytest

from scoring.opportunity_scorer import OpportunityScorer


@pytest.mark.parametrize("values,expected", [
    ((100, 100, 100, 100), 100.0),
    ((0, 0, 0, 0), 0.0),
    ((80, 70, 60, 50), 69.0),
    ((150, -10, 100, 100), 70.0),
])
def test_score(values, expected):
    assert OpportunityScorer.score(*values) == expected


@pytest.mark.parametrize("score,expected", [(85, "High"), (70, "Medium"), (59, "Low")])
def test_priority(score, expected):
    assert OpportunityScorer.priority(score) == expected
