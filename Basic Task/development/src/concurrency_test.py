import json
import time
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import urllib.request

HERE = Path(__file__).parent
RESULTS_DIR = (HERE / "../results").resolve()
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

URL = "http://localhost:8080/v1/chat/completions"

SYSTEM_PROMPT = "你为小型工作室提供办公文档处理与辅助编程服务。请按任务要求组织输出，区分资料中的事实、待确认信息与提出的建议。"

USER_PROMPT = "你是一家 8 人工作室的项目负责人。请给客户写一封项目延期邮件，说明调整原因、新安排和后续沟通方式，正文约 200 字。"

def one_request(idx):
    data = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT}
        ],
        "max_tokens": 256,
        "chat_template_kwargs": {"enable_thinking": False}
    }
    req = urllib.request.Request(
        URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            raw = resp.read()
        t1 = time.time()
        body = json.loads(raw.decode("utf-8"))
        usage = body.get("usage", {})
        timings = body.get("timings", {})
        return {
            "idx": idx,
            "ok": True,
            "wall_s": round(t1 - t0, 3),
            "completion_tokens": usage.get("completion_tokens", 0),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "prompt_ms": timings.get("prompt_ms", 0),
            "predicted_ms": timings.get("predicted_ms", 0),
            "predicted_per_second": timings.get("predicted_per_second", 0),
        }
    except Exception as e:
        return {"idx": idx, "ok": False, "wall_s": round(time.time() - t0, 3), "error": str(e)}

def run_concurrency(level, rounds=3):
    print(f"\n########## 并发 = {level} ##########")
    all_rounds = []
    for r in range(rounds):
        print(f"  --- 第 {r+1} 轮 ---")
        t_start = time.time()
        with ThreadPoolExecutor(max_workers=level) as pool:
            results = list(pool.map(one_request, range(level)))
        t_end = time.time()

        ok = [x for x in results if x["ok"]]
        fail = [x for x in results if not x["ok"]]
        total_tokens = sum(x.get("completion_tokens", 0) for x in ok)
        total_time = t_end - t_start

        round_summary = {
            "round": r + 1,
            "level": level,
            "success": len(ok),
            "fail": len(fail),
            "total_wall_s": round(total_time, 3),
            "total_completion_tokens": total_tokens,
            "aggregate_throughput_tps": round(total_tokens / total_time, 2) if total_time > 0 else 0,
            "avg_wall_s": round(sum(x["wall_s"] for x in ok) / len(ok), 3) if ok else None,
            "avg_predicted_tps": round(sum(x["predicted_per_second"] for x in ok) / len(ok), 2) if ok else None,
        }
        all_rounds.append(round_summary)
        print(f"    成功率 {len(ok)}/{level}, 总耗时 {total_time:.2f}s, "
              f"聚合吞吐 {round_summary['aggregate_throughput_tps']} t/s")
        for f in fail:
            print(f"    FAIL #{f['idx']}: {f.get('error')}")

    return all_rounds

def main():
    all_data = []
    for level in [1, 2, 4, 8, 10]:
        rounds = run_concurrency(level, rounds=3)
        all_data.extend(rounds)

    out = RESULTS_DIR / "concurrency_8slots.json"
    out.write_text(json.dumps(all_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== 结果已保存到 {out} ===")

if __name__ == "__main__":
    main()
