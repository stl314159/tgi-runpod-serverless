FROM ghcr.io/huggingface/text-generation-inference:latest

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git wget && \
    apt-get clean

RUN pip install -U pip
RUN pip install --upgrade text-generation runpod --no-cache-dir

WORKDIR /usr/src

COPY handler.py /usr/src/handler.py
COPY entrypoint.sh /usr/src/entrypoint.sh
COPY templates.py /usr/src/templates.py
COPY test_input.json /usr/src/test_input.json

RUN chmod +x /usr/src/entrypoint.sh

ENV HUGGINGFACE_HUB_CACHE /runpod-volume/hub
ENV TRANSFORMERS_CACHE /runpod-volume/hub
# ENV GPTQ_BITS 4
# ENV GPTQ_GROUPSIZE 1
# ENV NUM_GPU_SHARD 1
# ENV QUANTIZE 'gptq'

ENTRYPOINT [ "./entrypoint.sh" ]
