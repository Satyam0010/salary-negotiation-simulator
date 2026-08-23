"""Phase 1 finite negotiation workflow and persistent state helpers."""

import streamlit as st


MAX_ROUNDS = 7
TERMINAL_STATUSES = {"complete", "final"}


def build_candidate_profile(**values) -> dict:
    return values


def _append_turn(speaker: str, message: str, round_number: int, offer: int | None = None, score: int | None = None) -> None:
    turn = {"round": round_number, "speaker": speaker, "message": message}
    if offer is not None:
        turn["offer"] = offer
    if score is not None:
        turn["score"] = score
    st.session_state.negotiation_history.append(turn)


def start_simulation(profile: dict, turn_generator) -> None:
    initial_offer = round(profile["target_salary"] * 0.78)
    opening = turn_generator(profile, initial_offer, 1, [], "")
    opening = _normalize_turn(opening, 1, profile["target_salary"])

    st.session_state.simulation_started = True
    st.session_state.simulation_complete = False
    st.session_state.workflow_state = "HR_OPENING"
    st.session_state.negotiation_status = "ongoing"
    st.session_state.current_round = 1
    st.session_state.max_rounds = MAX_ROUNDS
    st.session_state.current_offer = initial_offer
    st.session_state.initial_offer = initial_offer
    st.session_state.target_salary = profile["target_salary"]
    st.session_state.counteroffers = [st.session_state.current_offer]
    st.session_state.negotiation_history = []
    st.session_state.score_history = []
    st.session_state.scores = {}
    st.session_state.performance_report = {}
    st.session_state.audio_transcript = ""
    _append_turn("HR", opening["hr_response"], 1, opening["counter_offer"])
    st.session_state.current_offer = opening["counter_offer"]
    st.session_state.negotiation_status = opening["negotiation_status"]
    if opening["negotiation_status"] in TERMINAL_STATUSES:
        st.session_state.workflow_state = "NEGOTIATION_COMPLETE"
        st.session_state.simulation_complete = True
    else:
        st.session_state.workflow_state = "CANDIDATE_RESPONSE"


def _normalize_turn(result: dict, expected_round: int, target_salary: int) -> dict:
    """Apply engine invariants to a validated or test-double AI response."""
    if not isinstance(result, dict):
        raise ValueError("The AI returned an invalid response.")
    required = {"hr_response", "counter_offer", "round", "negotiation_status", "candidate_argument_quality"}
    if not required.issubset(result):
        raise ValueError("The AI returned an incomplete response.")
    result = result.copy()
    result["round"] = expected_round
    result["counter_offer"] = max(1, min(int(result["counter_offer"]), int(target_salary)))
    result["negotiation_status"] = str(result["negotiation_status"]).lower()
    if result["negotiation_status"] not in {"ongoing", "complete", "final"}:
        raise ValueError("The AI returned an invalid negotiation status.")
    return result


def _candidate_ended_negotiation(response: str) -> bool:
    normalized = response.casefold().strip()
    return normalized in {"i accept", "accept", "i accept the offer", "end negotiation", "stop negotiation", "withdraw"}


def submit_text_response(response: str, turn_generator) -> None:
    profile = st.session_state.candidate_profile
    round_number = st.session_state.current_round
    if st.session_state.simulation_complete or st.session_state.workflow_state != "CANDIDATE_RESPONSE":
        return
    if _candidate_ended_negotiation(response) or round_number >= st.session_state.max_rounds:
        _append_turn("Candidate", response, round_number)
        st.session_state.user_arguments.append(response)
        st.session_state.negotiation_status = "complete"
        st.session_state.workflow_state = "NEGOTIATION_COMPLETE"
        st.session_state.simulation_complete = True
        return
    next_round = round_number + 1
    pending_history = [*st.session_state.negotiation_history, {"round": round_number, "speaker": "Candidate", "message": response}]
    result = turn_generator(profile, st.session_state.current_offer, next_round, pending_history, response)
    result = _normalize_turn(result, next_round, profile["target_salary"])
    _append_turn("Candidate", response, round_number)
    st.session_state.user_arguments.append(response)
    st.session_state.current_round = next_round
    st.session_state.current_offer = result["counter_offer"]
    st.session_state.counteroffers.append(result["counter_offer"])
    _append_turn("HR", result["hr_response"], next_round, result["counter_offer"], result["candidate_argument_quality"])
    st.session_state.score_history.append({"round": next_round, "candidate_argument_quality": result["candidate_argument_quality"]})
    st.session_state.negotiation_status = result["negotiation_status"]
    if result["negotiation_status"] in TERMINAL_STATUSES or next_round >= st.session_state.max_rounds:
        st.session_state.workflow_state = "NEGOTIATION_COMPLETE"
        st.session_state.simulation_complete = True
    else:
        st.session_state.workflow_state = "CANDIDATE_RESPONSE"
