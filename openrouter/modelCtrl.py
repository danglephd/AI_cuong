import os

import requests

OPENROUTER_API_KEY = os.getenv("api_key")

def get_free_models():
    url = "https://openrouter.ai/api/v1/models"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    data = response.json()["data"]

    free_models = []

    for model in data:
        pricing = model.get("pricing", {})

        # cách 1: pricing = 0
        if pricing.get("prompt") == "0" and pricing.get("completion") == "0":
            free_models.append(model["id"])
            continue

        # cách 2: suffix :free
        if model["id"].endswith(":free"):
            free_models.append(model["id"])

    return free_models


if __name__ == "__main__":
    models = get_free_models()
    print(f"Total free models: {len(models)}")
    for m in models[:20]:
        print(m)