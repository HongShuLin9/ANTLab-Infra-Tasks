import json
import urllib.request
from pathlib import Path
from flask import Flask, jsonify, send_from_directory

HERE = Path(__file__).parent
RESULTS_DIR = (HERE / "../../results").resolve()
LLAMA_URL = "http://localhost:8080"

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory(HERE, "index.html")

@app.route("/api/health")
def health():
    try:
        with urllib.request.urlopen(LLAMA_URL + "/v1/models", timeout=5) as r:
            data = json.loads(r.read().decode("utf-8"))
        return jsonify({"status": "ok", "model": data["data"][0]["id"]})
    except Exception as e:
        return jsonify({"status": "down", "error": str(e)})

@app.route("/api/summary")
def summary():
    p = RESULTS_DIR / "summary_baseline.json"
    if not p.exists():
        return jsonify({"error": "not found"}), 404
    return jsonify(json.loads(p.read_text(encoding="utf-8")))

@app.route("/api/concurrency")
def concurrency():
    out = {}
    for name in ["baseline", "8slots"]:
        p = RESULTS_DIR / f"concurrency_{name}.json"
        if p.exists():
            out[name] = json.loads(p.read_text(encoding="utf-8"))
    return jsonify(out)

@app.route("/api/task/<tid>")
def task_output(tid):
    p = RESULTS_DIR / f"{tid}_baseline" / "output.txt"
    if not p.exists():
        return jsonify({"error": "not found"}), 404
    return p.read_text(encoding="utf-8"), 200, {"Content-Type": "text/plain; charset=utf-8"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
