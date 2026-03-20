import requests #deepseek V3.2


url = "https://api.timeweb.cloud/api/v1/cloud-ai/agents/21add0ae-4fcb-4ffd-9d1e-8853fe779577/call"

def DeepSeek(prompt: str) -> str:
    # Ты подключишь nano / local / openai
    payload = {
        "message": f'{prompt}',
        "parent_message_id": "3adfea84-bcdb-44b5-8914-92035e75ec24"
    }
    #NOTUSEtoken = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoiaW5yb2IiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiJhMTY5YzgwZi0yYT>
    token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCIsImtpZCI6IjFrYnhacFJNQGJSI0tSbE1xS1lqIn0.eyJ1c2VyIjoiaW5yb2IiLCJ0eXBlIjoiYXBpX2tleSIsImFwaV9rZXlfaWQiOiI1N2YzZjg4Yi04ZDBkLTRiZDgtODI2ZC0wODczNTU2N2M1M2MiLCJpYXQiOjE3Njk1Njg4OTB9.ThrBoFuV8wI78OE5FK8UlCSTelIipA6VxA7JGbj6ywZM2UFyBCoWxEB_uVOeqGcDSCctK760n7072GW-_eRCblmomKY-tCp3GDNaMl7BQoHtVu0J666Qmq4BNRBRnqKbFr--d2KW-tpQ4gGxJeSgbvP7fjXmZtIRqbJuP09lmxzfO8Pnj2gOC0NxscP_J40_LtkqG0yZ8EKPSXiwGVWeB9oIOUv9k8KCcbIm49WDvczrTgcd19G4-uNcB3hymEPnZkx3BhnICqeWdewdvGTL4Xlsq9OJm_oOAYUoi30Kj51DWjhhqBt6tdNOQ9ALb7V_dZ12JIG_sQRBPpB2UVgpBWAHsuctfiofY5WzFQWriH8T4Tf1g2nXQLUp6-rigp_eyon_P8pLMhkJWlgzOB16GpdGGogS2Cpuc6XIhSzv1jVcmrXJE0Mzm7OVScNQg5Jmr3RrPlSRow31w7fCCQb78WYzJd7P0c1etyRzUyUO6jqS97A7VoSt_sYmQ4xmcfp9"
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    }
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if data["finish_reason"] == "stop":
        return data["message"]
    elif data["finish_reason"] == "length":
        return 0
    else:
        return 0


