from __future__ import print_function
import itertools as I
from dagflow import iterators, tools

def rshift(outputs, inputs):
    corresponding_outputs = tuple(iterators.iter_corresponding_outputs(inputs))
    for output, input in I.zip_longest(iterators.iter_outputs(outputs), iterators.iter_inputs(inputs), fillvalue=tools.undefinedleg):
        if not input or not output:
            raise Exception('Unable to connect mismatching lists')

        output.connect_to(input)

    if len(corresponding_outputs)==1:
        return corresponding_outputs[0]
    return corresponding_outputs

def lshift(inputs, outputs):
    return rshift(outputs, inputs)
