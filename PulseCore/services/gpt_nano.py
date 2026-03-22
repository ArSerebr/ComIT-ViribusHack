import os

import requests

from .gemini import _message_from_agent_response

url = "https://api.timeweb.cloud/api/v1/cloud-ai/agents/67ac01ab-90b3-4e70-bb11-3b9747072099/call"

_DEFAULT_TOKEN = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoiaW5yb2IiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiJhMTY5YzgwZi0yYTA4LTRiM2UtODg4My0wMDljMDlhOTNmNTQiLCJpYXQiOjE3Njk1MTc3NDN9.erIiCPKwY_geR3Aw9FEDZmp_-DuQfqgdSIWq6ZZW2JQqMveiZL3I4OWUONSeRZpmp0NjUFfkjHZ9qt8T_fmc0GsIZvJVO8LQfgQYdncrY5pNAfMEAnjpY9pMEJxvfvP8TNXKULdP54wEYWRmixQH7_YNXngJUn6P1ucmHVj8jAPsAvjHqFjnEtl0nzZDpEZQr0Cx12W1ddWoAZOua4hg6Bns9dHf0WFJnibKy9yGPZIRnZ-l54y0Z4AF8tgPlCAGLFNHVhnW-CopiXJLQkouHxk5yyvqwM2-_4nVPSZdgJHh8G_DNAuQHrw7aevHtXRABzC_FxJk8YHv4DoZtqEnV8gmVqLiICENNDFMMm4rMLEAy7ZOIcEJSlThjGa_yfkLLxMMuYAxJtjC0KeNqFUtf3-h9lukVsTKIPSaDu1pPXvIcQfaIVSieQ14GtxdoTYaIx5uv36z7ovJtmRefzTececTdSEcU-Szf1hup9Ni97N_gC5xp_OHAhozEKjDrP2t"


def GPT_nano(prompt: str) -> str:
    payload = {
        "message": f"{prompt}",
        "parent_message_id": "3adfea84-bcdb-44b5-8914-92035e75ec24",
    }
    token = os.environ.get("TIMEWEB_GPT_NANO_TOKEN", _DEFAULT_TOKEN)
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
    }
    response = requests.post(url, json=payload, headers=headers, timeout=120)
    return _message_from_agent_response(response, "GPT_nano")
