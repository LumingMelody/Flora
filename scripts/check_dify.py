import argparse
import json
import sys

import requests

from env import DIFY_API_KEY, DIFY_BASE_URL, DIFY_RESPONSE_MODE

DEFAULT_BASE_URL = DIFY_BASE_URL or "http://121.36.203.36:81/v1"


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Dify /workflows/run endpoint.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL, e.g. http://host:81/v1")
    parser.add_argument("--api-key", default=DIFY_API_KEY, help="Dify API key")
    parser.add_argument("--response-mode", default=DIFY_RESPONSE_MODE, help="blocking or streaming")
    parser.add_argument("--user", default="abc-123", help="User id")
    parser.add_argument("--inputs", default="{}", help="JSON string for inputs")
    args = parser.parse_args()

    if not args.base_url or not args.api_key:
        print("Missing base_url or api_key. Check .env or pass --base-url/--api-key.")
        return 2

    try:
        inputs = json.loads(args.inputs)
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON for --inputs: {exc}")
        return 2

    url = args.base_url.rstrip("/") + "/workflows/run"
    headers = {
        "Authorization": f"Bearer {args.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": inputs,
        "response_mode": args.response_mode,
        "user": args.user,
    }

    print(f"POST {url}")
    stream = args.response_mode == "streaming"
    with requests.post(url, json=payload, headers=headers, timeout=30, stream=stream) as resp:
        print(f"Status: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")
        if resp.status_code >= 400:
            print((resp.text or "")[:2000])
            return 0
        if stream:
            print("Streaming response (first 20 lines):")
            lines_printed = 0
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                print(line)
                lines_printed += 1
                if lines_printed >= 20:
                    break
            if lines_printed == 0:
                print("(no data)")
            return 0
        text = resp.text or ""
        if "application/json" in (resp.headers.get("Content-Type") or ""):
            try:
                print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
            except Exception:
                print(text)
        else:
            print(text[:2000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
