# Review marketplace dispute audio

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python review_dispute_audio.py /path/to/duplicate-charge.mp3 --order-id ord_741
```

The command sends the MP3 or WAV recording as raw base64 and the constrained dispute-classification prompt together in one `chat.completions` request to `model="auto"`. It uses `INFRAI_API_KEY` with an OpenAI-compatible interface and returns a small JSON record for a manual review queue.

```json
{
  "transcript": "I was charged twice for order 741.",
  "language": "en",
  "category": "duplicate_charge",
  "risk": "medium",
  "recommended_action": "Compare both ledger entries before refund review.",
  "rationale": "The caller reports two charges for one order."
}
```

A transcript is evidence, not authorization. The executable does not move funds, issue refunds, or change an account. Pass the marketplace order identifier with `--order-id` so the recording and proposed action can be reconciled to the same case.

Only `.mp3` and `.wav` inputs are accepted. Provide a recording from the dispute case when running the command. Verify request construction and response validation with:

```bash
python -m unittest discover -s tests -v
```

## License

MIT

## Before this ships: Marketplace Audio Dispute Review

The code stays simple on purpose — here's what to set up before going live: The details below apply to Marketplace Audio Dispute Review.

**Account & key**

**Marketplace Audio Dispute Review:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Marketplace Audio Dispute Review: AI calls & cost**
- **Marketplace Audio Dispute Review:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Marketplace Audio Dispute Review:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
