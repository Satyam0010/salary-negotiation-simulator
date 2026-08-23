"""Presentation helpers for the results dashboard."""

import pandas as pd
import streamlit as st

from analytics import negotiation_rounds_dataframe, round_score_dataframe, salary_progression_dataframe
from scoring import SCORE_WEIGHTS


def _apply_dashboard_styles() -> None:
	st.markdown(
		"""
		<style>
		.dashboard-kicker { color: #9a5b2f; font-size: .72rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
		[data-testid="stDataFrame"] { border: 1px solid #dedbd4; border-radius: 8px; overflow: hidden; }
		</style>
		""",
		unsafe_allow_html=True,
	)


def render_results_dashboard(profile: dict, report: dict, history: list[dict]) -> None:
	"""Render the completed negotiation as a compact assessment dashboard."""
	_apply_dashboard_styles()
	metrics = report["salary_metrics"]
	scores = report["category_scores"]
	rounds = sorted({item["round"] for item in history})

	st.divider()
	st.subheader("Negotiation complete")
	st.caption(f"{metrics['outcome'].title()} · {len(rounds)} rounds recorded")
	score_col, salary_col, target_col, rounds_col = st.columns(4)
	score_col.metric("Negotiation score", f"{report['overall_score']:.0f}/100", delta=f"{report['overall_score'] - 50:+.0f} vs baseline")
	salary_col.metric("Final salary", f"₹{metrics['final_salary']:,.0f}", delta=f"₹{metrics['salary_gain']:+,.0f} vs initial")
	target_col.metric("Target achievement", f"{metrics['target_achievement_percentage']:.1f}%", delta=f"{metrics['target_achievement_percentage'] - 100:+.1f} pp")
	rounds_col.metric("Rounds", str(len(rounds)), delta=f"{len(rounds) - 7:+d} vs maximum")

	st.markdown("#### Skill profile")
	score_frame = pd.DataFrame(
		[{"Skill": category.replace("_", " ").title(), "Score": scores[category], "Weight": f"{SCORE_WEIGHTS[category] * 100:.0f}%"} for category in SCORE_WEIGHTS]
	).set_index("Skill")
	st.bar_chart(score_frame[["Score"]], y_label="Score / 100", height=280)

	salary_col, round_col = st.columns(2)
	with salary_col:
		st.markdown("#### Salary progress")
		salary_frame = salary_progression_dataframe(metrics["initial_offer"], metrics["final_salary"], metrics["target_salary"])
		st.line_chart(salary_frame.set_index("stage"), y="salary", y_label="Monthly INR", height=260)
	with round_col:
		st.markdown("#### Round performance")
		round_frame = round_score_dataframe(history)
		if round_frame.empty:
			st.info("Round scores will appear after candidate responses are assessed.")
		else:
			st.line_chart(round_frame.set_index("round"), y="candidate_argument_quality", y_label="Argument quality", height=260)

	with st.expander("Candidate profile"):
		profile_frame = pd.DataFrame(
			[{"Field": key.replace("_", " ").title(), "Value": value} for key, value in profile.items() if key != "preparation_evidence"]
		)
		st.dataframe(profile_frame, width="stretch", hide_index=True)
	with st.expander("Round-by-round analysis"):
		st.dataframe(negotiation_rounds_dataframe(history), width="stretch", hide_index=True)
	with st.expander("AI feedback"):
		st.write(report["executive_summary"])
		st.markdown(f"**Strongest moment**  \n{report['strongest_moment']}")
		st.markdown(f"**Weakest moment**  \n{report['weakest_moment']}")
	with st.expander("Improvement plan"):
		for index, improvement in enumerate(report["improvements"], start=1):
			st.markdown(f"**{index}.** {improvement}")
	with st.expander("Scoring methodology"):
		st.write("Python calculates the overall score from validated Gemini category assessments.")
		st.dataframe(score_frame.reset_index(), width="stretch", hide_index=True)
		st.code("overall = persuasion*0.20 + evidence*0.20 + communication*0.15 + confidence*0.15 + strategy*0.15 + professionalism*0.15", language="text")
