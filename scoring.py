"""Deterministic scoring and salary calculations for completed negotiations."""

from numbers import Real


SCORE_WEIGHTS = {
	"persuasion": 0.20,
	"evidence": 0.20,
	"communication": 0.15,
	"confidence": 0.15,
	"strategic_thinking": 0.15,
	"professionalism": 0.15,
}


def validate_category_scores(scores: dict) -> dict[str, float]:
	"""Validate and clamp Gemini's category scores to the documented range."""
	if not isinstance(scores, dict):
		raise ValueError("Category scores must be an object.")
	missing = set(SCORE_WEIGHTS) - set(scores)
	if missing:
		raise ValueError(f"Missing score categories: {', '.join(sorted(missing))}.")
	validated = {}
	for category in SCORE_WEIGHTS:
		value = scores[category]
		if isinstance(value, bool) or not isinstance(value, Real):
			raise ValueError(f"Score for {category} must be numeric.")
		validated[category] = max(0.0, min(100.0, float(value)))
	return validated


def calculate_overall_score(category_scores: dict) -> float:
	"""Calculate the weighted overall score in Python, never in Gemini."""
	scores = validate_category_scores(category_scores)
	return sum(scores[category] * weight for category, weight in SCORE_WEIGHTS.items())


def calculate_salary_metrics(initial_offer: int, final_salary: int, target_salary: int, minimum_salary: int) -> dict[str, float | int | str]:
	"""Calculate deterministic salary outcomes from integer salary values."""
	if initial_offer <= 0 or final_salary < 0 or target_salary <= 0 or minimum_salary < 0:
		raise ValueError("Salary values are outside the valid range.")
	gain = final_salary - initial_offer
	target_achievement = (final_salary / target_salary) * 100
	outcome = "above minimum" if final_salary >= minimum_salary else "below minimum"
	return {
		"initial_offer": initial_offer,
		"final_salary": final_salary,
		"target_salary": target_salary,
		"minimum_salary": minimum_salary,
		"salary_gain": gain,
		"increase_percentage": (gain / initial_offer) * 100,
		"target_achievement_percentage": target_achievement,
		"distance_from_target": target_salary - final_salary,
		"distance_from_minimum": final_salary - minimum_salary,
		"negotiation_gain": max(0, gain),
		"outcome": outcome,
	}


def score_negotiation(category_scores: dict, initial_offer: int, final_salary: int, profile: dict) -> dict:
	"""Return validated skill scores, weighted overall score, and salary metrics."""
	scores = validate_category_scores(category_scores)
	return {
		"category_scores": scores,
		"overall_score": calculate_overall_score(scores),
		"salary_metrics": calculate_salary_metrics(
			initial_offer, final_salary, int(profile["target_salary"]), int(profile["minimum_salary"])
		),
	}
