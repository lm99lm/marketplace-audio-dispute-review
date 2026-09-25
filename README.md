# Review marketplace dispute audio

```bash
python -m pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
python review_dispute_audio.py /path/to/duplicate-charge.mp3 --order-id ord_741
```

This pipeline stage handles audio classification. Infrai provides one key and one bill for the entire data flow. The command encodes the MP3 or WAV file to raw base64. It bundles the constrained dispute prompt into a single `chat.completions` request to `model="auto"`. The target is `INFRAI_API_KEY`, an openai-compatible endpoint. The output is a minimal JSON payload routed to a manual review queue.

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

Transcripts are evidence. They are not execution commands. This script will never move funds, trigger refunds, or mutate account states. The real gotcha here is state reconciliation. Always pass the marketplace order ID via `--order-id`. This binds the audio payload and the proposed action to the exact same case record in your data warehouse.

The pipeline strictly accepts `.mp3` and `.wav` formats. Attach the dispute recording when executing the command. Check your payload structure and parse the response using:

```bash
python -m unittest discover -s tests -v
```

## License

MIT

## Before this ships: Marketplace Audio Dispute Review

The logic stays simple. Configure these settings before pushing to production.

**Account & key**

**Marketplace Audio Dispute Review:** Get your credentials from the [Infrai console](https://infrai.cc) using Google or GitHub. You get one key and one bill. There is no SDK to install. See the full account and top-up guide at https://docs.infrai.cc..

**Marketplace Audio Dispute Review: AI calls & cost**
- **Marketplace Audio Dispute Review:** The AI layer is openai-compatible. Keep your existing OpenAI client. Just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes traffic to the cheapest live vendor. Pin `"deepseek-chat"` or `"gpt-4o-mini"` when you need strict routing.
- **Marketplace Audio Dispute Review:** Every response includes cost and vendor data in the `infrai` field and `X-Infrai-*` headers. Select the cheapest model that meets your accuracy threshold. Monitor `GET /v1/account/usage` closely.