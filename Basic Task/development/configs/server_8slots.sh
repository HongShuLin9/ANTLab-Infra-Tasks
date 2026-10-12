#!/bin/bash
# ANTLab Basic Task - 8 slot 优化配置
# 对比基线：默认 4 slot
~/llama.cpp/build/bin/llama-server \
  -m ~/models/Qwen3-0.6B-Q8_0.gguf \
  -ngl 99 \
  -np 8 \
  --host 0.0.0.0 \
  --port 8080
