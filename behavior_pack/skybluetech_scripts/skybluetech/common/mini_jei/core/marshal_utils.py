# coding=utf-8
if 0:
    from .define import Input, Output


def MarshalInputs(inputs):
    # type: (dict[str, dict[int, Input]]) -> dict
    return {
        category: {slot: input.to_dict() for slot, input in inputs.items()}
        for category, inputs in inputs.items()
    }


def UnmarshalInputs(inputs):
    # type: (dict) -> dict[str, dict[int, Input]]
    return {
        category: {slot: Input.from_dict(input) for slot, input in inputs.items()}
        for category, inputs in inputs.items()
    }


def MarshalOutputs(outputs):
    # type: (dict[str, dict[int, Output]]) -> dict
    return {
        category: {slot: output.to_dict() for slot, output in outputs.items()}
        for category, outputs in outputs.items()
    }


def UnmarshalOutputs(outputs):
    # type: (dict) -> dict[str, dict[int, Output]]
    return {
        category: {slot: Output.from_dict(output) for slot, output in outputs.items()}
        for category, outputs in outputs.items()
    }
