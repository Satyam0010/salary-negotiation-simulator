"""Isolated Gemini client and structured response handling."""

import json
import logging
import os
import re
from typing import Any

import streamlit as st
from google import genai
from dotenv import load_dotenv

from prompts import HR_SYSTEM_PROMPT, build_assessment_prompt, build_round_prompt

LOGGER = logging.getLogger(__name__)
load_dotenv()


class GeminiServiceError(Exception):
    """A user-safe Gemini service failure."""


@st.cache_resource
def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        LOGGER.error("Gemini client unavailable: API key configured=false")
        raise GeminiServiceError("Gemini is not configured. Add GEMINI_API_KEY to your environment.")
    LOGGER.info("Gemini client configured: API key configured=true")
    return genai.Client(api_key=api_key)


def test_gemini_connection() -> str:
    """Make one explicit, minimal Gemini request for configuration testing."""
    try:
        response = get_gemini_client().models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents="Reply with exactly: Gemini connection successful.",
        )
        message = (response.text or "").strip()
        if not message:
            raise ValueError("The AI returned an empty response.")
        return message
    except GeminiServiceError:
        raise
    except Exception as error:
        raise GeminiServiceError("The Gemini service is unavailable. Check your key and try again.") from error


def _validate_response(payload: Any) -> dict:
    required = {"hr_response", "counter_offer", "round", "negotiation_status", "candidate_argument_quality", "hr_decision", "reason", "next_challenge"}
    if not isinstance(payload, dict) or not required.issubset(payload):
        raise ValueError("The AI returned an incomplete response.")
    if not isinstance(payload["hr_response"], str) or not payload["hr_response"].strip():
        raise ValueError("The AI returned an invalid HR response.")
    if payload["negotiation_status"] not in {"ongoing", "complete", "final"}:
        raise ValueError("The AI returned an invalid negotiation status.")
    if payload["hr_decision"] not in {"counter", "hold", "reject", "final"}:
        raise ValueError("The AI returned an invalid HR decision.")
    payload["counter_offer"] = int(payload["counter_offer"])
    if payload["counter_offer"] <= 0:
        raise ValueError("The AI returned an invalid counteroffer.")
    payload["round"] = int(payload["round"])
    if payload["round"] < 1:
        raise ValueError("The AI returned an invalid round.")
    quality = payload["candidate_argument_quality"]
    if isinstance(quality, str):
        quality = {"weak": 35, "fair": 55, "good": 75, "strong": 90}.get(quality.casefold().strip(), quality)
    payload["candidate_argument_quality"] = max(0, min(100, int(quality)))
    return payload


def _parse_json_response(text: str) -> dict:
    """Parse strict JSON while tolerating a fenced JSON block from the model."""
    cleaned = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        cleaned = fenced.group(1)
    payload = _validate_response(json.loads(cleaned))
    LOGGER.info("Gemini response parsing succeeded: structured fields validated")
    return payload


def _validate_assessment(payload: Any) -> dict:
    categories = {"persuasion", "evidence", "communication", "confidence", "strategic_thinking", "professionalism"}
    required = categories | {"executive_summary", "strongest_moment", "weakest_moment", "improvements"}
    if not isinstance(payload, dict) or not required.issubset(payload):
        raise ValueError("The AI returned an incomplete assessment.")
    for category in categories:
        value = payload[category]
        if isinstance(value, bool):
            raise ValueError("Assessment scores must be numeric.")
        payload[category] = max(0, min(100, float(value)))
    if not isinstance(payload["improvements"], list) or len(payload["improvements"]) != 3:
        raise ValueError("The assessment must contain exactly three improvements.")
    for field in ("executive_summary", "strongest_moment", "weakest_moment"):
        if not isinstance(payload[field], str) or not payload[field].strip():
            raise ValueError("The assessment contains empty feedback.")
    return payload


def generate_performance_assessment(profile: dict, history: list[dict]) -> dict:
    """Request category assessments; Python owns the final weighted score."""
    if not os.getenv("GEMINI_API_KEY"):
        raise GeminiServiceError("Gemini is required to generate the performance assessment.")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    try:
        LOGGER.info("Gemini API request started: operation=performance_assessment model=%s", model)
        response = get_gemini_client().models.generate_content(
            model=model,
            contents=build_assessment_prompt(profile, history),
            config={"response_mime_type": "application/json"},
        )
        payload = _validate_assessment(json.loads(response.text or ""))
        LOGGER.info("Gemini response parsing succeeded: operation=performance_assessment")
        return payload
    except GeminiServiceError:
        raise
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        LOGGER.exception("Gemini assessment parsing failed: error_type=%s", type(error).__name__)
        raise GeminiServiceError("Gemini returned an invalid performance assessment.") from error
    except Exception as error:
        LOGGER.exception("Gemini assessment request failed: error_type=%s", type(error).__name__)
        raise GeminiServiceError("The performance assessment service is unavailable.") from error


def generate_hr_turn(profile: dict, current_offer: int, current_round: int, history: list[dict], latest_response: str) -> dict:
    """Generate one structured HR turn, with a deterministic demo fallback."""
    if not os.getenv("GEMINI_API_KEY"):
        LOGGER.info("HR turn using demo fallback: API key configured=false round=%s", current_round)
        quality = 70 if len(latest_response.split()) >= 12 else 42
        counter_offer = min(profile["target_salary"], current_offer + (3000 if quality >= 60 else 1000))
        return {"hr_response": f"I hear your position. Please connect your request to measurable impact in your work. I can move to ₹{counter_offer:,.0f}, but I need stronger evidence to go further.", "counter_offer": counter_offer, "round": current_round, "negotiation_status": "ongoing", "candidate_argument_quality": quality, "hr_decision": "counter", "reason": "The response was assessed for specificity and evidence.", "next_challenge": "Quantify the result of your strongest achievement."}
    try:
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        LOGGER.info("Gemini API request started: operation=hr_turn model=%s round=%s", model, current_round)
        response = get_gemini_client().models.generate_content(
            model=model,
            contents=build_round_prompt(profile, current_offer, current_round, history, latest_response),
            config={"system_instruction": HR_SYSTEM_PROMPT, "response_mime_type": "application/json"},
        )
        LOGGER.info("Gemini API request succeeded: operation=hr_turn model=%s", model)
        return _parse_json_response(response.text or "")
    except (json.JSONDecodeError, ValueError, TypeError) as error:
        LOGGER.exception("Gemini response parsing failed: operation=hr_turn error_type=%s", type(error).__name__)
        raise GeminiServiceError("Gemini returned an invalid structured response. Please try again.") from error
    except GeminiServiceError:
        raise
    except Exception as error:
        LOGGER.exception("Gemini API request failed: operation=hr_turn error_type=%s", type(error).__name__)
        raise GeminiServiceError("The AI service is temporarily unavailable. Please try again.") from error
