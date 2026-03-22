import logging
import os

import requests

logger = logging.getLogger(__name__)

# Gemini 3 fast (Timeweb Cloud AI)
url = "https://api.timeweb.cloud/api/v1/cloud-ai/agents/add6dbbc-4878-4a20-9342-54b7d7bf6ac4/call"

_DEFAULT_TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoiaW5yb2IiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiJjNTVmODFiOC03OTgxLTQ4YTAtYWExNC0wYjY2N2E0YTIwMjgiLCJpYXQiOjE3Njk1MTU4NjV9.nJvuiHobJrhOMJZlo6-JNfFTpM47QyyPynMa4byY-mhdKtQhRlVz-GIp8nlUktQylA9rjd4Mtu6odwlLcySh7t9s5kDkn2d5cAP508LKBIJ5E5Y4je5iEf8IDPryUkGOvvfeIfUI1hGpslux9TIgRI17Ek2m9eHLrCNtT_iaRMsvkUIkGEqR-oIqFOrudsE1ErF8qkWQaaKakgEvl1a4L72Urgx8UXm1SxSWqGhytdrPx4ehJV2PSbvkuw7W3XJXV0311e9HCgMly9l1ccvgO54TiX5qXii9ZYkGZVu9ytqCxEYhBb3HCZqVBY0_NHmzhD7U6JLmNFP1NUFq7bNggFeT0j-L_EJmh7s7KErDcW_X-mr3FY9ln31iT9_D0iTdXyXFCGUPWsgCcCfVaqdqFTmPQre5T8A75JsCD6us17RSiyBUj_kpJ8hHe4ZDlR9nFQ-9QCn-hPtaPILle-3doWSlXzrQTYApljmCr_OB8CmL5-9lJ6_74CQNCcIBF5p7"


def _message_from_agent_response(response: requests.Response, agent_label: str) -> str:
    body_preview = (response.text or "")[:800]
    if not response.ok:
        logger.error("%s HTTP %s: %s", agent_label, response.status_code, body_preview)
        raise RuntimeError(f"{agent_label}: HTTP {response.status_code}")
    raw = (response.text or "").strip()
    if not raw:
        logger.error("%s empty response body", agent_label)
        raise RuntimeError(f"{agent_label}: empty response body")
    try:
        data = response.json()
    except ValueError as e:
        logger.error("%s non-JSON body: %s", agent_label, body_preview)
        raise RuntimeError(f"{agent_label}: response is not JSON") from e

    reason = data.get("finish_reason")
    msg = data.get("message")
    text = msg if isinstance(msg, str) else (str(msg) if msg is not None else "")

    if reason == "stop":
        return text
    if reason == "length":
        return text if text.strip() else ""
    logger.warning("%s unexpected finish_reason=%r", agent_label, reason)
    return text


def Gemini(prompt: str) -> str:
    payload = {
        "message": f"{prompt}",
        "parent_message_id": "3adfea84-bcdb-44b5-8914-92035e75ec24",
    }
    token = os.environ.get("TIMEWEB_GEMINI_TOKEN", _DEFAULT_TOKEN)
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }

    response = requests.post(url, json=payload, headers=headers, timeout=120)
    return _message_from_agent_response(response, "Gemini")
