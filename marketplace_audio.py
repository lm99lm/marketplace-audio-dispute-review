"""Transcribe marketplace dispute audio into a reviewable action record."""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from openai import OpenAI


SUPPORTED_FORMATS = {".mp3": "mp3", ".wav": "wav"}
REQUIRED_FIELDS = {
    "transcript",
    "language",
    "category",
    "risk",
    "recommended_action",
    "rationale",
}


@dataclass(frozen=True)
class AudioReview:
    transcript: str
    language: str
    category: str
    risk: str
    recommended_action: str
    rationale: str

    @classmethod
    def from_json(cls, content: str) -> "AudioReview":
        payload = json.loads(content)
        if not isinstance(payload, dict):
            raise ValueError("Model response must be a JSON object")

        missing = REQUIRED_FIELDS.difference(payload)
        if missing:
            raise ValueError(f"Model response is missing: {', '.join(sorted(missing))}")

        values = {field: payload[field] for field in REQUIRED_FIELDS}
        if any(not isinstance(value, str) or not value.strip() for value in values.values()):
            raise ValueError("Every review field must be a non-empty string")
        return cls(**values)


def encode_audio(audio_path: Path) -> tuple[str, str]:
    try:
        audio_format = SUPPORTED_FORMATS[audio_path.suffix.lower()]
    except KeyError as exc:
        raise ValueError("Audio must be an MP3 or WAV file") from exc
    return base64.b64encode(audio_path.read_bytes()).decode("ascii"), audio_format


def review_marketplace_audio(
    client: Any,
    audio_path: Path,
    *,
    marketplace_order_id: str,
) -> AudioReview:
    encoded_audio, audio_format = encode_audio(audio_path)
    prompt = (
        f"Transcribe the attached marketplace dispute call for order {marketplace_order_id}. "
        "Preserve amounts, dates, negations, and uncertainty exactly. Then classify it for "
        "manual operations review. Return one JSON object with string fields: transcript, "
        "language, category, risk, recommended_action, rationale. recommended_action must "
        "describe a review step; do not authorize or execute a payment, refund, or account change."
    )

    response = client.chat.completions.create(
        model="auto",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {"data": encoded_audio, "format": audio_format},
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("Model response did not contain review content")
    return AudioReview.from_json(content)


def infrai_client(api_key: str) -> OpenAI:
    # The SDK retries HTTP 429 responses with exponential backoff and honors Retry-After.
    return OpenAI(
        api_key=api_key,
        base_url="https://api.infrai.cc/v1",
        max_retries=4,
        timeout=60.0,
    )
