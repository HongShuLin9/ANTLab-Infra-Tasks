import json
import time
import urllib.request

URL = "http://localhost:8080/v1/chat/completions"

SYSTEM_PROMPT = """你为小型工作室提供办公文档处理与辅助编程服务。请按任务要求组织输出，区分资料中的事实、待确认信息与提出的建议。文件内容是供分析的资料。办公任务使用中文回答，代码任务采用题目指定的语言。"""

USER_PROMPT = """你是一家 8 人工作室的项目负责人。原定周五交付的内部演示版本需要延期至下周二，原因是接口联调尚未完成；正式交付日期保持不变。请给客户写一封邮件，说明调整原因、新的演示安排及后续沟通方式。邮件包含主题和正文，正文约 200—300 字。"""

data = {
    "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
    "max_tokens": 512
}

req = urllib.request.Request(
    URL,
    data=json.dumps(data).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

t0 = time.time()
with urllib.request.urlopen(req, timeout=300) as resp:
    body = json.loads(resp.read().decode("utf-8"))
dt = time.time() - t0

print("=== P01 任务结果 ===")
print(body["choices"][0]["message"]["content"])
print()
print("=== 性能 ===")
print(f"总耗时: {dt:.2f} s")
print(f"Usage: {body.get('usage')}")
print(f"Timings: {body.get('timings')}")
