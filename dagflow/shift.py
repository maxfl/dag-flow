from __future__ import print_function
import itertools as I
from dagflow import iterators, tools

def rshift(outputs, inputs):
    scope_id = id(locals())

    corresponding_outputs = tuple(iterators.iter_corresponding_outputs(inputs))
    for i, (output, input) in enumerate(I.zip_longest(iterators.iter_outputs(outputs), iterators.iter_inputs(inputs), fillvalue=tools.undefinedleg)):

        if not output:
            raise Exception('Unable to connect mismatching lists')

        if not input:
            missing_input_handler = getattr(inputs, 'missing_input_handler', lambda *args, **kwargs: None)
            input = missing_input_handler(scope=scope_id)

        output.connect_to(input)

    if len(corresponding_outputs)==1:
        return corresponding_outputs[0]

    return corresponding_outputs

def lshift(inputs, outputs):
    return rshift(outputs, inputs)
