"""第3回 宿題（基礎）: INSTRUCTIONS の1行を変えて、同じ質問のツール呼び出しと回答を比べる。

元の INSTRUCTIONS と「必ず search_glossary で用語集を確認する」の行を消した版で、
同じ質問を各2回実行し、ツール呼び出しと回答を JSON に保存する。

使い方:
    python scripts/lec03_basic.py
"""

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic_ai import Agent
from pydantic_ai.messages import ToolCallPart

from app import agent as base
from app import tools

QUESTIONS = [
    "LoRAとQLoRAの違いは？",
    "AIE2026の講座の宿題にある「3レベル」とは何ですか？",
]
REMOVED_LINE = "- 用語や講座に固有のことを答える前に、必ず search_glossary で用語集を確認する。\n"
REPEAT = 2
OUT = Path("lectures/03/basic_results.json")


def build(instructions: str) -> Agent:
    a = Agent(instructions=instructions)
    a.tool_plain(tools.search_glossary)
    a.tool_plain(tools.get_lecture_summary)
    return a


def main() -> None:
    assert REMOVED_LINE in base.INSTRUCTIONS
    variants = {
        "original": base.INSTRUCTIONS,
        "no_glossary_rule": base.INSTRUCTIONS.replace(REMOVED_LINE, ""),
    }
    model = base.build_model()
    results = []
    for name, instructions in variants.items():
        a = build(instructions)
        for question in QUESTIONS:
            for run in range(1, REPEAT + 1):
                result = a.run_sync(question, model=model)
                calls = [
                    {"tool": p.tool_name, "args": p.args}
                    for m in result.all_messages()
                    for p in m.parts
                    if isinstance(p, ToolCallPart)
                ]
                results.append(
                    {"variant": name, "question": question, "run": run,
                     "tool_calls": calls, "answer": result.output}
                )
                print(f"done: {name} run={run} calls={len(calls)} {question[:15]}")
                time.sleep(5)  # 無料枠のレート制限を避ける
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
