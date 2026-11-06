"""WhatsApp Business Cloud API adapter (Meta Graph API).

Modes
- "console" (default, no credentials): messages are logged and stored, nothing leaves the machine.
- "cloud": real sends through https://graph.facebook.com/{version}/{phone_number_id}/messages

Inbound webhook
- GET  verification: hub.mode=subscribe & hub.verify_token & hub.challenge
- POST deliveries: verify X-Hub-Signature-256 = HMAC-SHA256(app_secret, raw body)

Policy notes (2026): business-initiated messages outside the 24h window must be
approved *utility* templates (non-promotional, about the user's own loads);
zhol is a task-specific alerting service, not a general-purpose chatbot.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
from dataclasses import dataclass

import httpx

log = logging.getLogger("zhol.whatsapp")


@dataclass
class SendResult:
    ok: bool
    message_id: str | None = None
    error: str | None = None
    mode: str = "console"


class WhatsAppClient:
    def __init__(self, token: str | None = None, phone_number_id: str | None = None,
                 api_version: str = "v21.0", app_secret: str | None = None, verify_token: str | None = None,
                 http: httpx.Client | None = None):
        self.token = token
        self.phone_number_id = phone_number_id
        self.api_version = api_version
        self.app_secret = app_secret
        self.verify_token = verify_token
        self.mode = "cloud" if token and phone_number_id else "console"
        self._http = http

    @property
    def url(self) -> str:
        return f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"

    def _post(self, payload: dict) -> SendResult:
        if self.mode == "console":
            log.info("WHATSAPP (console) -> %s: %s", payload.get("to"), payload)
            return SendResult(ok=True, message_id=f"console-{abs(hash(str(payload))) % 10**10}", mode="console")
        client = self._http or httpx.Client(timeout=15.0)
        try:
            r = client.post(self.url, json=payload, headers={"Authorization": f"Bearer {self.token}"})
            data = r.json() if r.content else {}
            if r.status_code >= 400:
                err = data.get("error", {}).get("message", r.text)
                return SendResult(ok=False, error=f"{r.status_code}: {err}", mode="cloud")
            mid = (data.get("messages") or [{}])[0].get("id")
            return SendResult(ok=True, message_id=mid, mode="cloud")
        except httpx.HTTPError as exc:
            return SendResult(ok=False, error=str(exc), mode="cloud")
        finally:
            if self._http is None:
                client.close()

    def send_text(self, to: str, body: str) -> SendResult:
        return self._post({"messaging_product": "whatsapp", "recipient_type": "individual",
                           "to": to.lstrip("+"), "type": "text",
                           "text": {"preview_url": False, "body": body[:4096]}})

    def send_template(self, to: str, name: str, lang: str, params: list[str]) -> SendResult:
        return self._post({
            "messaging_product": "whatsapp", "to": to.lstrip("+"), "type": "template",
            "template": {"name": name, "language": {"code": "it" if lang == "it" else "en"},
                         "components": [{"type": "body",
                                         "parameters": [{"type": "text", "text": p[:1000]} for p in params]}]},
        })

    # -- webhook helpers
    def verify_subscription(self, mode: str | None, token: str | None, challenge: str | None) -> str | None:
        if mode == "subscribe" and self.verify_token and token == self.verify_token:
            return challenge
        return None

    def valid_signature(self, raw_body: bytes, header: str | None) -> bool:
        if not self.app_secret:
            return self.mode == "console"   # dev mode: accept unsigned test posts
        if not header or not header.startswith("sha256="):
            return False
        expected = hmac.new(self.app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, header.split("=", 1)[1])

    @staticmethod
    def parse_inbound(payload: dict) -> list[dict]:
        """Extract [{'from', 'text', 'id'}] from a Cloud API webhook payload."""
        out = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                for msg in change.get("value", {}).get("messages", []) or []:
                    text = ""
                    if msg.get("type") == "text":
                        text = msg.get("text", {}).get("body", "")
                    elif msg.get("type") == "button":
                        text = msg.get("button", {}).get("text", "")
                    elif msg.get("type") == "interactive":
                        it = msg.get("interactive", {})
                        text = (it.get("button_reply") or it.get("list_reply") or {}).get("title", "")
                    out.append({"from": msg.get("from"), "text": text, "id": msg.get("id")})
        return out
