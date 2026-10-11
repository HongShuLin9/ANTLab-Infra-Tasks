import json
import sys
import time
from pathlib import Path
import urllib.request

HERE = Path(__file__).parent
CFG = json.load(open(HERE / "../configs/tasks.json", encoding="utf-8"))
URL = "http://localhost:8080/v1/chat/completions"

INPUT_DIR = (HERE / CFG["input_dir"]).resolve()
RESULTS_DIR = (HERE / "../results").resolve()

def build_messages(task):
    system_prompt = CFG["system_prompt"]
    user_content = ""
    for fname in task["files"]:
        fpath = INPUT_DIR / fname
        if fpath.exists():
            content = fpath.read_text(encoding="utf-8")
            user_content += f"### 关联文件：{fname}\n\n{content}\n\n---\n\n"
    user_content += "### 任务\n\n" + task["prompt"]
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

def run_task(task):
    messages = build_messages(task)
    data = {
        "messages": messages,
        "max_tokens": CFG["max_tokens"],
        "chat_template_kwargs": {"enable_thinking": False}
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=900) as resp:
        body = json.loads(resp.read().decode("utf-8"))
    dt = time.time() - t0
    return body, dt

ids = sys.argv[1:]
print(f"Re-running: {ids}")

summary = []
for task in CFG["tasks"]:
    if task["id"] not in ids:
        continue
    tid = task["id"]
    print(f"\n=== Running {tid} ===")
    try:
        body, dt = run_task(task)
        content = body["choices"][0]["message"]["content"]
        usage = body.get("usage", {})
        timings = body.get("timings", {})

        out_dir = RESULTS_DIR / f"{tid}_baseline"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "output.txt").write_text(content, encoding="utf-8")
        (out_dir / "raw.json").write_text(
            json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        summary.append({
            "id": tid, "status": "ok",
            "latency_s": round(dt, 3),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens"),
            "prefill_tps": round(timings.get("prompt_per_second", 0), 2),
            "decode_tps": round(timings.get("predicted_per_second", 0), 2),
        })
        print(f"  OK: {dt:.2f}s, {usage.get('completion_tokens')} tokens, "
              f"decode {timings.get('predicted_per_second', 0):.1f} t/s")
    except Exception as e:
        summary.append({"id": tid, "status": "fail", "error": str(e)})
        print(f"  FAIL: {e}")

print("\n=== Result ===")
print(json.dumps(summary, ensure_ascii=False, indent=2))
