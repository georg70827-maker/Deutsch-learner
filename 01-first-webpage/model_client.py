import json
import os
import re
from pathlib import Path
from urllib import request


class ModelConfigurationError(RuntimeError):
    pass


def build_payload(messages):
    return {
        "model": os.getenv("MODEL_NAME", "deepseek-v4-flash"),
        "messages": messages,
        "temperature": 0.4,
    }


def generate(messages):
    api_url = os.getenv(
        "MODEL_API_URL", "https://api.deepseek.com/chat/completions"
    )
    api_key = os.getenv("MODEL_API_KEY")
    key_file = os.getenv(
        "MODEL_API_KEY_FILE",
        r"C:\Users\23009\OneDrive\Desktop\api.txt",
    )

    if not api_key and Path(key_file).is_file():
        file_content = Path(key_file).read_text(encoding="utf-8")
        match = re.search(r"sk-[A-Za-z0-9]+", file_content)
        api_key = match.group(0) if match else file_content.strip()

    if not api_key:
        raise ModelConfigurationError(
            "请设置 MODEL_API_KEY，或让 MODEL_API_KEY_FILE 指向密钥文件。"
        )

    body = json.dumps(build_payload(messages), ensure_ascii=False).encode("utf-8")
    http_request = request.Request(
        api_url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    with request.urlopen(http_request, timeout=60) as response:
        result = json.loads(response.read().decode("utf-8"))

    return result["choices"][0]["message"]["content"]
