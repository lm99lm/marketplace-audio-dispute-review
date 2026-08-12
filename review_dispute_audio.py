"""CLI entry point for a marketplace audio review."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from pathlib import Path

from marketplace_audio import infrai_client, review_marketplace_audio


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe a marketplace dispute call and prepare a manual review action."
    )
    parser.add_argument("audio", type=Path, help="Path to an MP3 or WAV recording")
    parser.add_argument("--order-id", required=True, help="Marketplace order identifier")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = infrai_client(os.environ["INFRAI_API_KEY"])
    review = review_marketplace_audio(
        client,
        args.audio,
        marketplace_order_id=args.order_id,
    )
    print(json.dumps(asdict(review), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
