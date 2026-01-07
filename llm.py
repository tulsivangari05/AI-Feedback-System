import requests
import json
import os
import time

# Load API key from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

PROMPT = """
You are a customer feedback assistant.

Given a restaurant review, produce the following in JSON:

1. user_response: a polite response shown to the user
2. summary: a short internal summary
3. action: recommended next action for admin

Review:
"{review}"

Return ONLY valid JSON, with no extra text:
{{
  "user_response": "...",
  "summary": "...",
  "action": "..."
}}
"""

def _call_openrouter_api(review_text):
    """Internal function to call OpenRouter API once"""
    payload = {
        "model": "meta-llama/llama-3-8b-instruct",
        "messages": [{"role": "user", "content": PROMPT.format(review=review_text)}]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=HEADERS,
        json=payload,
        timeout=20
    )
    response.raise_for_status()  # raise error if HTTP error
    result = response.json()

    content = result["choices"][0]["message"]["content"]

    # Try parsing JSON
    try:
        parsed = json.loads(content)
        # Ensure required keys exist
        for key in ["user_response", "summary", "action"]:
            if key not in parsed:
                parsed[key] = "N/A"
        return parsed
    except (json.JSONDecodeError, KeyError):
        # If JSON parsing fails, fallback
        return {
            "user_response": content.strip(),
            "summary": "Could not parse summary",
            "action": "Could not parse action"
        }

def process_review(review_text, retries=2, delay=1):
    """
    Call LLM API with retry logic.
    Returns a dict: {user_response, summary, action}
    """
    for attempt in range(retries + 1):
        try:
            return _call_openrouter_api(review_text)
        except requests.RequestException as e:
            if attempt < retries:
                time.sleep(delay)
                continue
            else:
                # If all retries fail
                return {
                    "user_response": review_text,
                    "summary": "AI service unavailable",
                    "action": "Admin review required"
                }

# if __name__ == "__main__":
#     test_review = "The food was good and service was excellent."
#     result = process_review(test_review)
#     print(result)
