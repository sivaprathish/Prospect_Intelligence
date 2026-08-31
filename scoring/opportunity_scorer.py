"""Deterministic opportunity scoring."""

from __future__ import annotations


class OpportunityScorer:
    WEIGHTS = {
        "signal_strength": 0.35,
        "pain_point_relevance": 0.30,
        "business_fit": 0.25,
        "recency": 0.10,
    }

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(float(value), 100.0))

    @classmethod
    def score(
        cls,
        signal_strength: float,
        pain_point_relevance: float,
        business_fit: float,
        recency: float,
    ) -> float:
        result = (
            cls._clamp(signal_strength) * cls.WEIGHTS["signal_strength"]
            + cls._clamp(pain_point_relevance) * cls.WEIGHTS["pain_point_relevance"]
            + cls._clamp(business_fit) * cls.WEIGHTS["business_fit"]
            + cls._clamp(recency) * cls.WEIGHTS["recency"]
        )
        return round(result, 2)

    @staticmethod
    def priority(score: float) -> str:
        if score >= 80:
            return "High"
        if score >= 60:
            return "Medium"
        return "Low"
