"""Presentation helpers for the results dashboard."""

import pandas as pd
import streamlit as st

from analytics import negotiation_rounds_dataframe, round_score_dataframe, salary_progression_dataframe
from scoring import SCORE_WEIGHTS


def apply_theme() -> None:
	"""Apply the single light, high-contrast theme used by every screen."""
	st.markdown(
		"""
		<style>
		:root { --canvas:#f7f8fa; --surface:#ffffff; --ink:#111827; --secondary:#4b5563; --muted:#6b7280; --line:#d1d5db; --accent:#b4533f; --accent-hover:#913d30; --accent-soft:#f8ebe8; }
		.stApp { background:var(--canvas); color:var(--ink); }
		.block-container { max-width:1120px; padding:2.25rem 2rem 4rem; }
		h1,h2,h3,h4,h5,h6,p,label,[data-testid="stWidgetLabel"] p { color:var(--ink) !important; }
		h1 { font-size:2.55rem; line-height:1.12; letter-spacing:0; } h2 { font-size:1.7rem; } h3 { font-size:1.3rem; } h4 { font-size:1rem; }
		[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color:var(--secondary) !important; }
		[data-testid="stForm"], [data-testid="stExpander"], [data-testid="stMetric"], [data-testid="stDataFrame"] { background:var(--surface); border:1px solid var(--line); border-radius:8px; }
		[data-testid="stForm"] { padding:1.2rem; } [data-testid="stMetric"] { padding:1rem; } [data-testid="stMetricLabel"] { color:var(--secondary) !important; } [data-testid="stMetricValue"] { color:var(--ink) !important; }
		[data-baseweb="input"] > div, [data-baseweb="textarea"] > div, [data-baseweb="select"] > div { background:var(--surface) !important; border:1px solid var(--line) !important; border-radius:6px; }
		[data-baseweb="input"] input, [data-baseweb="textarea"] textarea, [data-baseweb="select"] *, [data-testid="stNumberInput"] input { background:var(--surface) !important; color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; }
		[data-baseweb="input"] input::placeholder, [data-baseweb="textarea"] textarea::placeholder, textarea::placeholder { color:var(--muted) !important; opacity:1 !important; -webkit-text-fill-color:var(--muted) !important; }
		textarea { background:var(--surface) !important; color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; caret-color:var(--accent); }
		[data-baseweb="input"]:focus-within > div, [data-baseweb="textarea"]:focus-within > div, [data-baseweb="select"]:focus-within > div { border-color:var(--accent) !important; box-shadow:0 0 0 1px var(--accent); }
		.stButton > button, [data-testid="stFormSubmitButton"] > button { background:var(--surface) !important; color:var(--ink) !important; border:1px solid var(--line) !important; border-radius:6px; font-weight:650; min-height:2.6rem; }
		.stButton > button *, [data-testid="stFormSubmitButton"] > button * { color:inherit !important; -webkit-text-fill-color:currentColor !important; }
		.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover { background:var(--accent-soft) !important; color:var(--ink) !important; border-color:var(--accent) !important; }
		.stButton > button:focus-visible, [data-testid="stFormSubmitButton"] > button:focus-visible { outline:3px solid var(--accent-soft); outline-offset:2px; }
		button[kind="primary"], button[kind="primaryFormSubmit"], button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"] { background:var(--accent) !important; color:#fff !important; border-color:var(--accent) !important; }
		button[kind="primary"] *, button[kind="primaryFormSubmit"] *, button[data-testid="stBaseButton-primary"] *, button[data-testid="stBaseButton-primaryFormSubmit"] * { color:#fff !important; -webkit-text-fill-color:#fff !important; }
		button[kind="primary"]:hover, button[kind="primaryFormSubmit"]:hover, button[data-testid="stBaseButton-primary"]:hover, button[data-testid="stBaseButton-primaryFormSubmit"]:hover { background:var(--accent-hover) !important; border-color:var(--accent-hover) !important; color:#fff !important; }
		button:disabled { background:#e5e7eb !important; color:var(--secondary) !important; border-color:#c5cad1 !important; opacity:1 !important; }
		[data-testid="stAudioInput"] button, [data-testid="stAudioInput"] button:hover { background:var(--accent) !important; color:#fff !important; border-color:var(--accent) !important; } [data-testid="stAudioInput"] button * { color:#fff !important; }
		[data-testid="stExpander"] summary, [data-testid="stExpander"] summary p, [data-testid="stAlert"] { color:var(--ink) !important; }
		.hero { border-bottom:1px solid var(--line); padding-bottom:1.75rem; margin-bottom:2rem; } .eyebrow { color:var(--accent); font-size:.72rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; } .hero p { color:var(--secondary); font-size:1.05rem; }
		@media (max-width:720px) { .block-container { padding:1.4rem 1rem 3rem; } h1 { font-size:2.15rem; } }
		</style>
		""", unsafe_allow_html=True,
	)


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
