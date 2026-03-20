import requests #Claude Haiku

url = ""

def Haiku(prompt: str) -> str:
    payload = {
        "message": f'{prompt}',
        "parent_message_id": "3adfea84-bcdb-44b5-8914-92035e75ec24"
    }
    token = ""
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    if data["finish_reason"] == "stop":
        return data["message"]
    elif data["finish_reason"] == "length":
        return "0"
    else:
        return "0"

