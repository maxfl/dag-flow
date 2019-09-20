from __future__ import print_function
from dagflow import legs, input as Input, output as Output
from dagflow.tools import IsIterable

def iter_inputs(inputs):
    if isinstance(inputs, Input.Input):
        yield inputs
    else:
        if isinstance(inputs, dict):
            iterable = inputs.values()
        elif IsIterable(inputs):
            iterable = inputs
        elif isinstance(inputs, legs.Legs):
            iterable = inputs._iter_inputs()
        else:
            raise Exception('Do not know how to iterate inputs')

        for input in iterable:
            for input1 in iter_inputs(input):
                yield input1

def iter_outputs(outputs):
    if isinstance(outputs, Output.Output):
        yield outputs
    else:
        if isinstance(outputs, dict):
            iterable = outputs.values()
        elif IsIterable(outputs):
            iterable = outputs
        elif isinstance(outputs, legs.Legs):
            iterable = outputs._iter_outputs()
        else:
            raise Exception('Do not know how to iterate outputs')

        for output in iterable:
            for output1 in iter_outputs(output):
                yield output1

def iter_corresponding_outputs(inputs):
    if isinstance(inputs, Input.Input):
        yield inputs.corresponding_output()
    elif isinstance(inputs, Output.Output):
        yield inputs
    else:
        if isinstance(inputs, dict):
            iterable = inputs.values()
        elif IsIterable(inputs):
            iterable = inputs
        elif isinstance(inputs, legs.Legs):
            yield inputs
            return
        else:
            raise Exception('Do not know how to iterate corresponding outputs')

        for output in iterable:
            for output1 in iter_corresponding_outputs(output):
                yield output1
