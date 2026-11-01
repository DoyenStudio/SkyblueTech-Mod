# coding=utf-8
if 0 > 1:
    from .define import Input, Output

# JSON serializable


def MarshalOrderedInputs(all_inputs):
    # type: (dict[str, dict[int, Input]]) -> dict[str, dict[str, dict]]
    return {
        category: {str(slot): input.to_dict() for slot, input in inputs.items()}
        for category, inputs in all_inputs.items()
    }


def MarshalUnorderedInputs(all_inputs):
    # type: (dict[str, dict[tuple[int, ...], list[Input]]]) -> dict[str, dict[str, list[dict]]]
    return {
        category: {
            ",".join(str(i) for i in slots): [i.to_dict() for i in input_list]
            for slots, input_list in inputs.items()
            if slots
        }
        for category, inputs in all_inputs.items()
    }


def UnmarshalOrderedInputs(all_inputs):
    # type: (dict[str, dict[str, dict]]) -> dict[str, dict[int, Input]]
    from .define import Input

    return {
        category: {int(slot): Input.from_dict(input) for slot, input in inputs.items()}
        for category, inputs in all_inputs.items()
    }


def UnmarshalUnorderedInputs(all_inputs):
    # type: (dict[str, dict[str, list[dict]]]) -> dict[str, dict[tuple[int, ...], list[Input]]]
    from .define import Input

    return {
        category: {
            tuple(int(i) for i in slots.split(",")): [
                Input.from_dict(i) for i in input_list
            ]
            for slots, input_list in inputs.items()
        }
        for category, inputs in all_inputs.items()
    }


def MarshalOrderedOutputs(all_outputs):
    # type: (dict[str, dict[int, Output]]) -> dict[str, dict[str, dict]]
    return {
        category: {str(slot): output.to_dict() for slot, output in outputs.items()}
        for category, outputs in all_outputs.items()
    }


def MarshalUnorderedOutputs(all_outputs):
    # type: (dict[str, dict[tuple[int, ...], list[Output]]]) -> dict[str, dict[str, list[dict]]]
    return {
        category: {
            ",".join(str(i) for i in slots): [o.to_dict() for o in output_list]
            for slots, output_list in outputs.items()
            if slots
        }
        for category, outputs in all_outputs.items()
    }


def UnmarshalOrderedOutputs(all_outputs):
    # type: (dict[str, dict[str, dict]]) -> dict[str, dict[int, Output]]
    from .define import Output

    return {
        category: {
            int(slot): Output.from_dict(output) for slot, output in outputs.items()
        }
        for category, outputs in all_outputs.items()
    }


def UnmarshalUnorderedOutputs(all_outputs):
    # type: (dict[str, dict[str, list[dict]]]) -> dict[str, dict[tuple[int, ...], list[Output]]]
    from .define import Output

    return {
        category: {
            tuple(int(i) for i in slots.split(",")): [
                Output.from_dict(o) for o in output_list
            ]
            for slots, output_list in outputs.items()
        }
        for category, outputs in all_outputs.items()
    }
