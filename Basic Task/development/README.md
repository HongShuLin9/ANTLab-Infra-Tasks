# ANTLab Infra - Basic Task

## 方向与提交信息

- 方向：Infra
- 分支：master
- commit SHA：见 GitHub 仓库最新提交

## 模型信息

- 模型：Qwen3-0.6B-GGUF Q8_0
- 文件大小：约 604 MiB
- 参数量：596M
- 下载：https://modelscope.cn/models/Qwen/Qwen3-0.6B-GGUF
- 存储位置：~/models/Qwen3-0.6B-Q8_0.gguf

## 运行入口

启动推理服务（基线 4 slot）：
bash configs/server_baseline.sh

启动推理服务（优化 8 slot）：
bash configs/server_8slots.sh

批量执行 10 个任务：
cd src && python3 runner.py

并发测试：
python3 concurrency_test.py

错误恢复测试：
python3 recover.py

前端展示：
python3 web/app.py

## 报告位置

- reports/报告.md — 书面报告
- reports/并发对比.png — 并发吞吐对比图

## 测试数据位置

- results/summary_baseline.json — 10 任务基线汇总
- results/concurrency_baseline.json — 4 slot 并发数据
- results/concurrency_8slots.json — 8 slot 并发数据
- results/recovery_log.json — 错误恢复时间线
- results/<ID>_baseline/output.txt — 各任务模型输出

## 主要优化

slot 数从 4 增加到 8，并发 8 时聚合吞吐从 309 t/s 提升到 644 t/s（+108%）。代价是每 slot 上下文从 40960 降到 10496。

## 复现步骤

见 reports/报告.md 第 12 节。
