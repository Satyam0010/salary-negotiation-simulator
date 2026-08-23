"""Centralized, idempotent Streamlit session-state initialization."""

import streamlit as st


SESSION_STATE_DEFAULTS = {
    "simulation_started": False,
    "workflow_state": "CONFIGURATION",
    "negotiation_status": "not_started",
    "negotiation_history": [],
    "current_round": 0,
    "current_offer": 0,
    "initial_offer": 0,
    "target_salary": 0,
    "counteroffers": [],
    "user_arguments": [],
    "audio_transcript": "",
    "scores": {},
    "score_history": [],
    "performance_report": {},
    "candidate_profile": {},
    "preparation_evidence": [],
    "simulation_complete": False,
    "max_rounds": 7,
}


def initialize_session_state() -> None:
    """Create missing keys without replacing values across Streamlit reruns."""
    for key, default in SESSION_STATE_DEFAULTS.items():
        if key not in st.session_state:
            if isinstance(default, (dict, list)):
                st.session_state[key] = default.copy()
            else:
                st.session_state[key] = default
