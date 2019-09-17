from __future__ import print_function
import itertools as I

def rshift(outputs, inputs):
    corresponding_outputs = tuple(iter_corresponding_outputs(inputs))
    for output, input in I.zip_longest(iter_outputs(outputs), iter_inputs(inputs), fillvalue=undefinedleg):
        if output is undefinedleg or input is undefinedleg:
            raise Exception('Unable to connect mismatching lists')

        output.connect_to(input)

    if len(corresponding_outputs)==1:
        return corresponding_outputs[0]
    return corresponding_outputs

def lshift(inputs, outputs):
    return rshift(outputs, inputs)
