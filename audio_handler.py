"""Audio input adapter for the shared negotiation workflow."""

import logging
import os

from google.genai import types

from gemini_client import GeminiServiceError, get_gemini_client

LOGGER = logging.getLogger(__name__)


def transcribe_audio(audio_input) -> str:
	"""Transcribe one Streamlit audio upload with Gemini and return plain text."""
	if audio_input is None:
		raise ValueError("Record an audio response before analyzing it.")

	audio_bytes = audio_input.getvalue()
	if not audio_bytes:
		raise ValueError("The recorded audio was empty. Please record your response again.")

	mime_type = getattr(audio_input, "mime_type", None) or "audio/wav"
	model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
	LOGGER.info("Audio transcription request started: model=%s mime_type=%s bytes=%s", model, mime_type, len(audio_bytes))
	try:
		response = get_gemini_client().models.generate_content(
			model=model,
			contents=[
				"Transcribe the candidate's spoken response exactly. Return only the transcript, without commentary.",
				types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
			],
		)
		transcript = (response.text or "").strip()
		if not transcript:
			raise ValueError("Gemini returned an empty transcript.")
		LOGGER.info("Audio transcription request succeeded: transcript_present=true")
		return transcript
	except GeminiServiceError:
		raise
	except ValueError:
		raise
	except Exception as error:
		LOGGER.exception("Audio transcription request failed: error_type=%s", type(error).__name__)
		raise GeminiServiceError("The audio could not be transcribed. Please try again.") from error
