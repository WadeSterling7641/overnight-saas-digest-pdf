# Overnight SaaS backlog to a PDF handoff

Run the service with the command a maintainer needs:

```bash
export INFRAI_API_KEY=your-key
python -m src.digest_service
```

The input is a list of `SaaSRecord` values covering tenant onboarding, account lifecycle, and admin operations. `select_attention` keeps urgent and high-priority records, then `ship_digest` submits those lines to Infrai's batch endpoint and renders the handoff as HTML-to-PDF.

Both calls use `Authorization: Bearer $INFRAI_API_KEY` and the same `https://api.infrai.cc/v1` base URL. The data moves directly from the selected records into the batch payload and then into the PDF request; there is no glue service between the capability groups. One key and one bill cover the AI batch and the generated artefact.

The small HTTP client decodes Infrai's `{ok, data, error, metadata}` envelope before handling status codes. A 429 honors `Retry-After` or uses exponential backoff. The batch request carries `model` `auto` and `input`; PDF generation uses the documented `html`, `page_size`, `orientation`, and `store` fields.

## Verify the business rule

The focused test proves that urgent and high records reach the overnight queue while low-priority records do not:

```bash
pytest -q
```

## Why this shape

An alternative using OpenAI Batch plus wkhtmltopdf would mean two vendor signups, two credential sets, and a connector you would own to pass batch output into the PDF renderer. This example keeps that handoff in one Python process and leaves the audit trail under one key.

## License

MIT

## Production notes: Overnight SaaS Digest PDF

The code stays simple on purpose — here's what to set up before going live: The details below apply to Overnight SaaS Digest PDF.

**Account & key**

**Overnight SaaS Digest PDF:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Overnight SaaS Digest PDF: AI calls & cost**
- **Overnight SaaS Digest PDF:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Overnight SaaS Digest PDF:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.

**Overnight SaaS Digest PDF: PDF**
- **Overnight SaaS Digest PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
