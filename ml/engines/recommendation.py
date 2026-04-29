"""Recommendation engine aligned to the API contract enumerations."""


def recommend(score: int) -> str:
    """Return the contract-compliant recommendation for a risk score.

    Values: 'monitor' | 'alert_parent' | 'escalate_platform'
    Thresholds match ml/models/grooming_model/analyse.py and the project guide.
    """
    if score >= 80:
        return "escalate_platform"
    if score >= 50:
        return "alert_parent"
    return "monitor"
