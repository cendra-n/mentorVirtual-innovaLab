import urllib.request
import urllib.error
import json

api_key = "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"
url = "https://api.anthropic.com/v1/messages"

def test_model(model_name):
    print(f"Testing model: {model_name}...")
    payload = json.dumps({
        "model": model_name,
        "max_tokens": 50,
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"SUCCESS: {model_name}")
            print(data)
            return True
    except urllib.error.HTTPError as he:
        print(f"FAILED: {model_name} -> HTTPError {he.code}: {he.reason}")
        try:
            print("Response body:", he.read().decode("utf-8"))
        except Exception as read_err:
            print("Could not read response body:", read_err)
        return False
    except Exception as e:
        print(f"FAILED: {model_name} -> {e}")
        return False

# Test the custom models from the banner!
test_model("claude-fable-5")
test_model("claude-mythos-5")
