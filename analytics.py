"""Pandas transformations for round, score, and salary analytics."""

import pandas as pd


def negotiation_rounds_dataframe(history: list[dict]) -> pd.DataFrame:
	"""Create a stable table of every persisted interaction."""
	columns = ["round", "speaker", "message", "offer", "score"]
	return pd.DataFrame(history, columns=columns)


def round_score_dataframe(history: list[dict]) -> pd.DataFrame:
	"""Create one candidate quality observation per round."""
	rows = [
		{"round": item["round"], "candidate_argument_quality": item["score"]}
		for item in history
		if item.get("speaker") == "HR" and item.get("score") is not None
	]
	return pd.DataFrame(rows, columns=["round", "candidate_argument_quality"])


def salary_progression_dataframe(initial_offer: int, final_salary: int, target_salary: int) -> pd.DataFrame:
	"""Represent the offer path used by salary visualizations."""
	return pd.DataFrame(
		[
			{"stage": "Initial offer", "salary": initial_offer},
			{"stage": "Final salary", "salary": final_salary},
			{"stage": "Target salary", "salary": target_salary},
		]
	)
