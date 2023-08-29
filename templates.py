class Template():
    def __init__(self, template_method):
        self.template_method = template_method

    def __call__(self, prompt):
        return self.template_method(prompt)


LLAMA_TEMPLATE = Template(
    lambda prompt: """SYSTEM: You are a helpful assistant.
USER: {}
ASSISTANT: """.format(prompt)
)

WIZARDCODER_TEMPLATE = Template(
    lambda prompt: """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{}

### Response: """.format(prompt)
)

DEFAULT_TEMPLATE = Template(
    lambda prompt: prompt
)