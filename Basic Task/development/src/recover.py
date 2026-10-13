import json
import subprocess
import time
from pathlib import Path
import urllib.request

HERE = Path(__file__).parent
RESULTS_DIR = (HERE / "../results").resolve()
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

LLAMA_BIN = Path.home() / "llama.cpp/build/bin/llama-server"
MODEL = Path.home() / "models/Qwen3-0.6B-Q8_0.gguf"
LOG = Path.home() / "llama-server-recover.log"

def check_health():
    try:
        with urllib.request.urlopen("http://localhost:8080/v1/models", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False

def start_server():
    cmd = [
        "nohup", str(LLAMA_BIN),
        "-m", str(MODEL),
        "-ngl", "99",
        "-np", "8",
        "--host", "0.0.0.0",
        "--port", "8080",
    ]
    with open(LOG, "ab") as f:
        subprocess.Popen(cmd, stdout=f, stderr=f)
    print(f"  已启动服务，日志写入 {LOG}")

def wait_health(timeout=30):
    t0 = time.time()
    while time.time() - t0 < timeout:
        if check_health():
            return True
        time.sleep(1)
    return False

def test_request():
    data = {
        "messages": [{"role": "user", "content": "你好"}],
        "max_tokens": 16,
        "chat_template_kwargs": {"enable_thinking": False}
    }
    req = urllib.request.Request(
        "http://localhost:8080/v1/chat/completions",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.loads(r.read().decode("utf-8"))
        return {"ok": True, "latency_s": round(time.time() - t0, 3),
                "content": body["choices"][0]["message"]["content"][:100]}
    except Exception as e:
        return {"ok": False, "error": str(e)}

events = []
def log_event(kind, detail):
    events.append({
        "time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "event": kind,
        "detail": detail,
    })
    print(f"[{events[-1]['time']}] {kind}: {detail}")

print("=== 步骤 1: 初始健康检查 ===")
healthy = check_health()
log_event("health_check", f"healthy={healthy}")

print("\n=== 步骤 2: 如果健康，故意停掉服务（模拟异常）===")
if healthy:
    subprocess.run(["pkill", "-f", "llama-server"])
    log_event("stop", "手动停止 llama-server")
    time.sleep(2)
    healthy_after_stop = check_health()
    log_event("health_check", f"after stop, healthy={healthy_after_stop}")
else:
    log_event("skip_stop", "服务本来就没跑，跳过停止步骤")

print("\n=== 步骤 3: 恢复服务 ===")
if not check_health():
    t0 = time.time()
    start_server()
    log_event("restart", "调用 start_server")
    ok = wait_health(timeout=30)
    recovery_time = round(time.time() - t0, 2)
    log_event("recovery", f"恢复耗时 {recovery_time}s, 成功={ok}")
else:
    recovery_time = 0
    log_event("skip_restart", "服务已经在跑")

print("\n=== 步骤 4: 恢复后验证 ===")
result = test_request()
log_event("verify", json.dumps(result, ensure_ascii=False))

out = RESULTS_DIR / "recovery_log.json"
out.write_text(json.dumps({
    "events": events,
    "recovery_time_s": recovery_time,
    "final_request": result,
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n=== 记录已保存到 {out} ===")
