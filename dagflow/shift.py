from __future__ import print_function
import itertools as I
from dagflow import iterators, tools

# Python2 compatibility
zip_longest = getattr(I, 'zip_longest', None)
if not zip_longest:
    zip_longest = getattr(I, 'izip_longest')

_rshift_scope_id = 0
def rshift_scope_id():
    global _rshift_scope_id
    ret=_rshift_scope_id
    _rshift_scope_id+=1
    return ret

def rshift(outputs, inputs):
    scope_id = rshift_scope_id()

    for i, (output, input) in enumerate(zip_longest(iterators.iter_outputs(outputs),
                                                    iterators.iter_inputs(inputs, True),
                                                    fillvalue=tools.undefinedleg)):
        if not output:
            raise Exception('Unable to connect mismatching lists')

        if not input:
            missing_input_handler = getattr(inputs, 'missing_input_handler', lambda *args, **kwargs: None)
            input = missing_input_handler(scope=scope_id)

        output._connect_to(input)

    corresponding_outputs = tuple(iterators.iter_corresponding_outputs(inputs))

    if len(corresponding_outputs)==1:
        return corresponding_outputs[0]

    return corresponding_outputs

def lshift(inputs, outputs):
    return rshift(outputs, inputs)
