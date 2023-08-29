#!/bin/bash

if [[ -z "${MODEL_ID}" ]]; then
  echo "MODEL_ID must be set"
  exit 1
fi

# Read NUM_GPU_SHARD env var, default to 1
if [[ -z "${NUM_GPU_SHARD}" ]]; then
  NUM_GPU_SHARD=1
fi

# Read QUANTIZE env var, default to qptq
if [[ -z "${QUANTIZE}" ]]; then
  QUANTIZE='gptq'
fi

GPTQ_BITS=4 GPTQ_GROUPSIZE=1 text-generation-launcher --quantize $QUANTIZE  --num-shard $NUM_GPU_SHARD &

# Delay until the TGI server is online
while ! wget -q --spider http://localhost:80/docs; do
    echo "Waiting for TGI server to start listening on port 80"
    sleep 1
done

echo "TGI Server is listening on port 80"

RUNPOD_DEBUG_LEVEL='DEBUG' RUNPOD_DEBUG='true' python -m handler.py