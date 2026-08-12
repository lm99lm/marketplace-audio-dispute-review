import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from marketplace_audio import review_marketplace_audio


class RecordingCompletions:
    def __init__(self) -> None:
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        content = json.dumps(
            {
                "transcript": "I was charged twice for order 741.",
                "language": "en",
                "category": "duplicate_charge",
                "risk": "medium",
                "recommended_action": "Compare both ledger entries before refund review.",
                "rationale": "The caller reports two charges for one order.",
            }
        )
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )


class MarketplaceAudioTest(unittest.TestCase):
    def test_builds_audio_request_and_parses_review(self) -> None:
        completions = RecordingCompletions()
        client = SimpleNamespace(
            chat=SimpleNamespace(completions=completions)
        )

        with tempfile.TemporaryDirectory() as directory:
            audio_path = Path(directory) / "claim.wav"
            audio_path.write_bytes(b"RIFF-test-audio")
            review = review_marketplace_audio(
                client,
                audio_path,
                marketplace_order_id="ord_741",
            )

        self.assertEqual(review.category, "duplicate_charge")
        self.assertEqual(completions.request["model"], "auto")
        audio_part = completions.request["messages"][0]["content"][0]
        self.assertEqual(audio_part["type"], "input_audio")
        self.assertEqual(audio_part["input_audio"]["format"], "wav")


if __name__ == "__main__":
    unittest.main()
