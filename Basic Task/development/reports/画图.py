import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
RESULTS = (HERE / "../results").resolve()

def avg_by_level(rows):
    m = {}
    for x in rows:
        m.setdefault(x["level"], []).append(x["aggregate_throughput_tps"])
    return {k: sum(v)/len(v) for k, v in m.items()}

base = json.loads((RESULTS / "concurrency_baseline.json").read_text())
opt = json.loads((RESULTS / "concurrency_8slots.json").read_text())
b = avg_by_level(base)
o = avg_by_level(opt)

levels = [1, 2, 4, 8, 10]
bv = [b.get(l, 0) for l in levels]
ov = [o.get(l, 0) for l in levels]

# 中文字体
plt.rcParams["font.sans-serif"] = ["DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

x = range(len(levels))
width = 0.35
fig, ax = plt.subplots(figsize=(8, 5))
ax.bar([i - width/2 for i in x], bv, width, label="4 slot (baseline)", color="#4a90e2")
ax.bar([i + width/2 for i in x], ov, width, label="8 slot (optimized)", color="#14803c")
ax.set_xticks(list(x))
ax.set_xticklabels([f"C{c}" for c in levels])
ax.set_xlabel("Concurrency")
ax.set_ylabel("Aggregate throughput (tokens/s)")
ax.set_title("Concurrency Throughput: 4 slot vs 8 slot")
ax.legend()

for i, (a, bb) in enumerate(zip(bv, ov)):
    ax.text(i - width/2, a + 10, f"{a:.0f}", ha="center", fontsize=9)
    ax.text(i + width/2, bb + 10, f"{bb:.0f}", ha="center", fontsize=9)

plt.tight_layout()
out = HERE / "并发对比.png"
plt.savefig(out, dpi=140)
print("saved:", out)
