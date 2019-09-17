from __future__ import print_function
from collections import OrderedDict
import dagflow
from tools import IsIterable

def iter_inputs(inputs):
    if isinstance(inputs, dagflow.Input):
        yield inputs
    else:
        if isinstance(inputs, OrderedDict):
            iterable = inputs.values()
        elif IsIterable(inputs):
            iterable = inputs
        elif isinstance(inputs, dagflow.Legs):
            iterable = inputs._iter_inputs()
        else:
            raise Exception('Do not know how to iterate inputs')

        for input in iterable:
            for input1 in iter_inputs(input):
                yield input1

def iter_outputs(outputs):
    if isinstance(outputs, dagflow.Output):
        yield outputs
    else:
        if isinstance(outputs, OrderedDict):
            iterable = outputs.values()
        elif IsIterable(outputs):
            iterable = outputs
        elif isinstance(outputs, dagflow.Legs):
            iterable = outputs._iter_outputs()
        else:
            raise Exception('Do not know how to iterate outputs')

        for output in iterable:
            for output1 in iter_outputs(output):
                yield output1

def iter_corresponding_outputs(inputs):
    if isinstance(inputs, dagflow.Input):
        yield inputs.corresponding_output()
    elif isinstance(inputs, dagflow.Output):
        yield inputs
    else:
        if isinstance(inputs, OrderedDict):
            iterable = inputs.values()
        elif IsIterable(inputs):
            iterable = inputs
        elif isinstance(inputs, dagflow.Legs):
            yield inputs
            return
        else:
            raise Exception('Do not know how to iterate corresponding outputs')

        for output in iterable:
            for output1 in iter_corresponding_outputs(output):
                yield output1
