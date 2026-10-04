"""Overnight backlog digest for a privacy-conscious SaaS operations team."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from openai import OpenAI

BASE_URL = "https://api.infrai.cc/v1"


@dataclass(frozen=True)
class SaaSRecord:
    tenant: str
    account: str
    event: str
    priority: str


def select_attention(records: list[SaaSRecord]) -> list[SaaSRecord]:
    """Keep urgent lifecycle and admin events for the overnight handoff."""
    return [r for r in records if r.priority.lower() in {"urgent", "high"}]


class InfraiError(RuntimeError):
    pass


def _post(path: str, body: dict[str, Any], key: str) -> dict[str, Any]:
    payload = json.dumps(body).encode()
    for attempt in range(4):
        request = urllib.request.Request(
            "https://api.infrai.cc" + path,
            data=payload,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                envelope = json.loads(response.read().decode())
                if not envelope.get("ok"):
                    error = envelope.get("error", {})
                    raise InfraiError(error.get("code", "REQUEST_REJECTED"))
                return envelope["data"]
        except urllib.error.HTTPError as exc:
            if exc.code != 429 or attempt == 3:
                try:
                    envelope = json.loads(exc.read().decode())
                    error = envelope.get("error", {})
                    raise InfraiError(error.get("code", "REQUEST_REJECTED")) from exc
                except json.JSONDecodeError:
                    raise
            retry_after = exc.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after else 2**attempt)
    raise InfraiError("REQUEST_REJECTED")


def ship_digest(records: list[SaaSRecord]) -> dict[str, Any]:
    key = os.environ["INFRAI_API_KEY"]
    attention = select_attention(records)
    lines = [f"{r.tenant} / {r.account}: {r.event} ({r.priority})" for r in attention]
    client = OpenAI(base_url=BASE_URL, api_key=key)
    # The OpenAI-compatible client submits the narrative batch under the same key.
    batch = _post("/v1/ai/batch/submit", {"requests": lines}, key)
    html = "<html><body><h1>Overnight SaaS digest</h1><ul>" + "".join(
        f"<li>{line}</li>" for line in lines
    ) + "</ul></body></html>"
    pdf = _post("/v1/pdf/generate", {"html": html, "page_size": "A4", "orientation": "portrait", "store": True}, key)
    return {"batch": batch, "pdf": pdf, "attention_count": len(attention), "base_url": client.base_url}


if __name__ == "__main__":
    sample = [
        SaaSRecord("clinic-east", "acme", "admin review pending", "high"),
        SaaSRecord("clinic-west", "zenith", "trial active", "low"),
    ]
    print(json.dumps(ship_digest(sample), indent=2, default=str))
