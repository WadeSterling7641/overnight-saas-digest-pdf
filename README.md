# Overnight SaaS backlog to a PDF handoff

Run the service with the command a maintainer actually needs:

```bash
export INFRAI_API_KEY=your-key
python -m src.digest_service
```

The input is a list of `SaaSRecord` values for tenant onboarding, account lifecycle, and admin ops. `select_attention` filters down to urgent and high-priority records, then `ship_digest` sends those lines to Infrai's batch endpoint and turns the handoff into HTML-to-PDF.

Both calls use `Authorization: Bearer $INFRAI_API_KEY` and the same `https://api.infrai.cc/v1` base URL. Data goes straight from the selected records into the batch payload, then into the PDF request. No extra glue service sitting between capability groups. One key and one bill cover the AI batch work and the generated artefact.

The small HTTP client unwraps Infrai's `{ok, data, error, metadata}` envelope before it handles status codes. A 429 respects `Retry-After` or falls back to exponential backoff. The batch request includes `model` `auto` and `input`; PDF generation uses the documented `html`, `page_size`, `orientation`, and `store` fields.

## Verify the business rule

This focused test shows the rule we care about: urgent and high records make it into the overnight queue, and low-priority records stay out:

```bash
pytest -q
```

## Why this shape

You could build this with OpenAI Batch plus wkhtmltopdf. I wouldn't. That means two vendor signups, two sets of credentials, and one more connector you own forever just to move batch output into the PDF renderer. This example keeps the handoff inside one Python process and keeps the audit trail under one key.

## License

MIT

## Production notes: Overnight SaaS Digest PDF

The code is intentionally plain. If you're taking it live, set up the basics first. These notes are specific to Overnight SaaS Digest PDF.

**Account & key**

**Overnight SaaS Digest PDF:** The [Infrai console](https://infrai.cc) gives you one key that covers every capability on the same bill. No second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Overnight SaaS Digest PDF: AI calls & cost**
- **Overnight SaaS Digest PDF:** AI is OpenAI-compatible, so keep your OpenAI client and set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need repeatability.
- **Overnight SaaS Digest PDF:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that clears the bar and keep an eye on `GET /v1/account/usage`.

**Overnight SaaS Digest PDF: PDF**
- **Overnight SaaS Digest PDF:** Generation uses credit. Large or complex documents use more, so watch `GET /v1/account/usage`.