"""Salary Negotiation Simulator - Phase 1 Streamlit shell."""

import os
import logging

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from audio_handler import transcribe_audio
from gemini_client import GeminiServiceError, generate_hr_turn, generate_performance_assessment, test_gemini_connection
from negotiation_engine import (
    build_candidate_profile,
    start_simulation,
    submit_text_response,
)
from session_state import initialize_session_state
from scoring import score_negotiation
from ui import apply_theme, render_results_dashboard

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
st.set_page_config(page_title="Salary Negotiation Simulator", page_icon="₹", layout="wide")
initialize_session_state()

apply_theme()
st.markdown('<div class="hero"><div class="eyebrow">Professional practice console</div><h1>Salary Negotiation Simulator</h1><p>Practice the conversation before the real conversation.</p></div>', unsafe_allow_html=True)

if not st.session_state.simulation_started:
    st.subheader("Prepare your profile")
    st.caption("Build your case before you enter the conversation. Gemini is not called while you edit this form.")
    with st.expander("Test Gemini connection"):
        st.caption("This sends one small request only when you press the button.")
        if st.button("Send test request"):
            try:
                result = test_gemini_connection()
                st.success(result)
            except GeminiServiceError as error:
                st.error(str(error))
    with st.form("candidate_profile_form"):
        candidate_name = st.text_input("Candidate name", placeholder="Your name")
        left, right = st.columns(2)
        with left:
            job_role = st.text_input("Job role", value="Software Engineer")
            experience = st.number_input("Years of experience", min_value=0.0, max_value=40.0, value=2.0, step=0.5)
            current_salary = st.number_input("Current / previous monthly salary (INR)", min_value=0, value=70000, step=1000)
            expected_salary = st.number_input("Expected monthly salary (INR)", min_value=0, value=96400, step=1000)
        with right:
            minimum_salary = st.number_input("Minimum acceptable monthly salary (INR)", min_value=0, value=82000, step=1000)
            target_salary = st.number_input("Target monthly salary (INR)", min_value=0, value=96400, step=1000)
            key_skills = st.text_input("Key skills", placeholder="Python, APIs, cloud")
            achievements = st.text_area("Major achievements", placeholder="Describe measurable impact")
        st.markdown("#### Negotiation evidence")
        st.caption("Record the proof behind your strongest points. Refine this table before starting.")
        evidence_defaults = st.session_state.preparation_evidence or [
            {"Negotiation point": "Technical impact", "Evidence": "", "Priority": "High"},
            {"Negotiation point": "Relevant experience", "Evidence": "", "Priority": "Medium"},
            {"Negotiation point": "Market rationale", "Evidence": "", "Priority": "Medium"},
        ]
        preparation_evidence = st.data_editor(
            pd.DataFrame(evidence_defaults),
            num_rows="dynamic",
            width="stretch",
            column_config={
                "Negotiation point": st.column_config.TextColumn("Negotiation point", required=True),
                "Evidence": st.column_config.TextColumn("Evidence", help="Use measurable results, scope, or examples."),
                "Priority": st.column_config.SelectboxColumn("Priority", options=["High", "Medium", "Low"], required=True),
            },
            key="preparation_evidence_editor",
        )
        negotiation_style = st.selectbox("Preferred negotiation style", ["Data-driven", "Confident", "Collaborative", "Assertive"])
        difficulty = st.selectbox("Difficulty level", ["Easy", "Medium", "Hard", "Expert"], index=1)
        submitted = st.form_submit_button("Start Simulation", type="primary")

    if submitted:
        if not candidate_name.strip():
            st.error("Enter your name to begin.")
        elif any(value < 0 for value in [current_salary, expected_salary, minimum_salary, target_salary]):
            st.error("Salary values cannot be negative.")
        elif target_salary < minimum_salary:
            st.error("Target salary must be at least the minimum acceptable salary.")
        else:
            profile = build_candidate_profile(
                candidate_name=candidate_name.strip(), job_role=job_role.strip() or "Software Engineer",
                experience=experience, current_salary=current_salary, expected_salary=expected_salary,
                minimum_salary=minimum_salary, target_salary=target_salary, key_skills=key_skills.strip(),
                achievements=achievements.strip(), negotiation_style=negotiation_style, difficulty=difficulty,
            )
            evidence = preparation_evidence.fillna("").to_dict(orient="records")
            evidence = [
                {key: str(value).strip() for key, value in item.items()}
                for item in evidence
                if str(item.get("Negotiation point", "")).strip()
            ]
            if not evidence:
                st.error("Add at least one negotiation point to your preparation evidence.")
                st.stop()
            profile["preparation_evidence"] = evidence
            st.session_state.candidate_profile = profile
            st.session_state.preparation_evidence = evidence
            try:
                start_simulation(profile, generate_hr_turn)
            except GeminiServiceError as error:
                st.error(str(error))
            except ValueError:
                st.error("The HR manager returned an invalid negotiation response. Please try again.")
            else:
                st.rerun()
else:
    profile = st.session_state.candidate_profile
    st.caption(f"{profile['job_role']} · {profile['difficulty']} difficulty")
    round_col, offer_col = st.columns(2)
    round_col.metric("Round", f"{st.session_state.current_round} / {st.session_state.max_rounds}")
    offer_col.metric("Current offer", f"₹{st.session_state.current_offer:,.0f}")

    st.subheader("HR Manager")
    if st.session_state.negotiation_history:
        latest_hr = next((item for item in reversed(st.session_state.negotiation_history) if item["speaker"] == "HR"), None)
        if latest_hr:
            st.info(latest_hr["message"])

    st.subheader("Your response")
    with st.form("response_form", clear_on_submit=True):
        response = st.text_area("Make your case", placeholder="Explain the value and evidence behind your request.", label_visibility="collapsed")
        response_submitted = st.form_submit_button("Submit Response", type="primary")
    if response_submitted:
        if not response.strip():
            st.warning("Write a response before submitting.")
        else:
            try:
                submit_text_response(response.strip(), generate_hr_turn)
                st.rerun()
            except GeminiServiceError as error:
                st.error(str(error))
            except ValueError:
                st.error("The HR manager returned an invalid negotiation response. Please try again.")

    st.subheader("Or respond by voice")
    with st.form("audio_response_form"):
        audio_response = st.audio_input("Record your response")
        audio_submitted = st.form_submit_button("Analyze Audio", type="primary")
    if audio_submitted:
        try:
            transcript = transcribe_audio(audio_response)
            st.session_state.audio_transcript = transcript
            submit_text_response(transcript, generate_hr_turn)
            st.rerun()
        except GeminiServiceError as error:
            st.error(str(error))
        except ValueError as error:
            st.error(str(error))

    if st.session_state.audio_transcript:
        with st.expander("Latest audio transcript", expanded=True):
            st.write(st.session_state.audio_transcript)

    with st.expander("Negotiation transcript"):
        for item in st.session_state.negotiation_history:
            label = "HR Manager" if item["speaker"] == "HR" else "You"
            st.markdown(f"**Round {item['round']} · {label}**")
            st.write(item["message"])

    if st.session_state.simulation_complete:
        st.success("This practice negotiation is complete. Results and scoring will be added in a later phase.")
        if st.button("Generate Performance Report"):
            try:
                assessment = generate_performance_assessment(profile, st.session_state.negotiation_history)
                report = score_negotiation(
                    {key: assessment[key] for key in ("persuasion", "evidence", "communication", "confidence", "strategic_thinking", "professionalism")},
                    st.session_state.initial_offer, st.session_state.current_offer, profile,
                )
                st.session_state.scores = report["category_scores"]
                st.session_state.performance_report = {**assessment, **report}
                st.rerun()
            except GeminiServiceError as error:
                st.error(str(error))
            except ValueError:
                st.error("The performance assessment returned invalid scores. Please try again.")
        if st.session_state.performance_report:
            render_results_dashboard(profile, st.session_state.performance_report, st.session_state.negotiation_history)
    if not os.getenv("GEMINI_API_KEY"):
        st.caption("Demo mode: add GEMINI_API_KEY to use Gemini responses.")
