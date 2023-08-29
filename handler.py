import runpod
import os
from text_generation import AsyncClient, Client
from templates import DEFAULT_TEMPLATE, LLAMA_TEMPLATE, WIZARDCODER_TEMPLATE
from copy import copy
import inspect
import warnings
import asyncio
import time
from json import loads

DEFAULT_GENERATE_PARAMS = loads(os.getenv("DEFAULT_GENERATE_PARAMS", "{}"))

class RequestCounter:
    """
    A concurrency controller that keeps track of the number of concurrent requests.
    """
    def __init__(self):
        self.counter = 0

    def increment(self):
        self.counter += 1

    def decrement(self):
        self.counter -= 1

request_counter = RequestCounter()

def concurrency_controller() -> bool:
    # Indicate whether there are any active requests
    return request_counter.counter > 0

# Create the text-generation-inference asynchronous client
client = Client(base_url="http://localhost:80", timeout=600)

# Get valid arguments for generate and generate_stream
valid_non_stream_arguments = inspect.getfullargspec(client.generate).args
valid_stream_arguments = inspect.getfullargspec(client.generate_stream).args

# Verify that the default generate parameters are valid
temp_default_generate_params = copy(DEFAULT_GENERATE_PARAMS)
for key in DEFAULT_GENERATE_PARAMS.keys():
    if key not in valid_non_stream_arguments and key not in valid_stream_arguments:
        warnings.warn(f"Warning: Invalid generate parameter: {key} passed in DEFAULT_GENERATE_PARAMS. Removing from DEFAULT_GENERATE_PARAMS.")
        raise ValueError(
            f"Invalid generate parameter: {key}. Valid parameters are: {valid_non_stream_arguments + valid_stream_arguments}"
        )
    temp_default_generate_params.pop(key)
DEFAULT_GENERATE_PARAMS = temp_default_generate_params


def handler(job):
    '''
    This is the handler function that will be called by the serverless worker.
    '''
    request_counter.increment()
    print(f"Starting request {job}, active requests: {request_counter.counter}")
    start = time.time()

    # Get job input
    job_input = job['input']
    prompt = job_input['prompt']

    # Set Generate Params
    generate_params = copy(DEFAULT_GENERATE_PARAMS)
    generate_params.update(job_input.pop('generate_params', {}))

    # Set Stream Option
    stream = job_input.pop('stream', False)

    # Print the prompt and generate_params
    print("**** PROMPT ****")
    print(prompt)
    print("**** GENERATE PARAMS ****")
    print(generate_params)
    print(f"**** STREAMING: {stream} ****")

    # Send request to Text Generation Inference Server and yield results
    result = client.generate(prompt, max_new_tokens=500)

    # Decrement the request counter
    request_counter.decrement()
    print(f"Finished request in {int(time.time() - start)} seconds, active requests: {request_counter.counter}")

    return result.generated_text


# Start the serverless worker
print("Starting the TGI serverless worker with streaming enabled.")
runpod.serverless.start(
    {"handler": handler, "concurrency_controller": concurrency_controller}
)
