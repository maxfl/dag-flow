from __future__ import print_function
from dagflow import input as Input, output as Output, shift

class Legs(object):
    def __init__(self, inputs=None, outputs=None):
        object.__init__(self)

        self.inputs = Input.Inputs(inputs)
        self.outputs = Output.Outputs(outputs)

    def __getitem__(self, key):
        if len(key)!=2:
            raise Exception('Legs key should be of length 2')

        ikey, okey = key

        if ikey and okey:
            if isinstance(ikey, (int, str)):
                ikey = ikey,
            if isinstance(okey, (int, str)):
                okey = okey,
            return Legs(self.inputs[ikey], self.outputs[okey])

        if ikey:
            return self.inputs[ikey]

        if okey:
            return self.outputs[okey]

        raise Exception('Empty keys specified')

    def __str__(self):
        return '->[{}],[{}]->'.format(len(self.inputs), len(self.outputs))

    def _iter_outputs(self):
        return iter(self.outputs)

    def _iter_inputs(self):
        return iter(self.inputs)

    def print(self):
        for i, input in enumerate(self.inputs):
            print(i, input)

        for i, output in enumerate(self.outputs):
            print(i, output)

    def __rshift__(self, other):
        return shift.rshift(self, other)

    def __rlshift__(self, other):
        return shift.rshift(self, other)

    def __lshift__(self, other):
        return shift.lshift(self, other)

    def __rrshift__(self, other):
        return shift.lshift(self, other)
