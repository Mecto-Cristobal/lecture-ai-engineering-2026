"""第1回 宿題（基礎）: 同じ質問を temperature を変えて3回ずつ実行し、結果をJSONに保存する。

使い方:
    GEMINI_API_KEY=... uv run python scripts/lec01_basic.py
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from google import genai
from google.genai import types

from app.config import MODEL, get_api_key

QUESTIONS = [
    "LoRAとは何ですか？",
    "AIE2026の講座の宿題にある「3レベル」とは何ですか？",
]
TEMPERATURES = [0.0, 1.0]
REPEAT = 3
OUT = Path("lectures/01/basic_results.json")


def main() -> None:
    client = genai.Client(api_key=get_api_key())
    results = []
    for question in QUESTIONS:
        for temperature in TEMPERATURES:
            for run in range(1, REPEAT + 1):
                response = client.models.generate_content(
                    model=MODEL,
                    contents=question,
                    config=types.GenerateContentConfig(temperature=temperature),
                )
                results.append(
                    {
                        "model": MODEL,
                        "question": question,
                        "temperature": temperature,
                        "run": run,
                        "text": response.text,
                    }
                )
                print(f"done: T={temperature} run={run} {question[:20]}")
                time.sleep(4)  # 無料枠のレート制限を避ける
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
