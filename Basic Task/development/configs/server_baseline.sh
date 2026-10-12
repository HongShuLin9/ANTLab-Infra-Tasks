#!/bin/bash
# ANTLab Basic Task - 基线配置（4 slot）
~/llama.cpp/build/bin/llama-server \
  -m ~/models/Qwen3-0.6B-Q8_0.gguf \
  -ngl 99 \
  --host 0.0.0.0 \
  --port 8080
