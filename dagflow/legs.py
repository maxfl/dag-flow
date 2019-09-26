from __future__ import print_function
from dagflow import shift
from dagflow.tools import StopNesting
from dagflow import input_extra

class Legs(object):
    __missing_input_handler = None
    def __init__(self, inputs=None, outputs=None, missing_input_handler=None):
        object.__init__(self)
        self._missing_input_handler = missing_input_handler

        from dagflow import input, output
        self.inputs = input.Inputs(inputs)
        self.outputs = output.Outputs(outputs)

    @property
    def _missing_input_handler(self):
        return self.__missing_input_handler

    @_missing_input_handler.setter
    def _missing_input_handler(self, handler):
        if handler:
            if isinstance(handler, str):
                sethandler = getattr(input_extra, handler)(self)
            elif isinstance(handler, type):
                sethandler = handler(self)
            else:
                sethandler = handler
                sethandler.node = self
        else:
            sethandler = input_extra.MissingInputFail(self)

        self.__missing_input_handler = sethandler

    def __getitem__(self, key):
        if isinstance(key, (int, slice, str)):
            return self.outputs[key]

        if len(key)!=2:
            raise Exception('Legs key should be of length 2')

        ikey, okey = key

        if ikey and okey:
            if isinstance(ikey, (int, str)):
                ikey = ikey,
            if isinstance(okey, (int, str)):
                okey = okey,
            return Legs(self.inputs[ikey], self.outputs[okey], missing_input_handler=self.__missing_input_handler)

        if ikey:
            return self.inputs[ikey]

        if okey:
            return self.outputs[okey]

        raise Exception('Empty keys specified')

    def __str__(self):
        return '->[{}],[{}]->'.format(len(self.inputs), len(self.outputs))

    def _deep_iter_outputs(self):
        return iter(self.outputs)

    def _deep_iter_inputs(self, disconnected_only=False):
        return iter(self.inputs)

    def _deep_iter_corresponding_outputs(self):
        raise StopNesting(self)

    def print(self):
        for i, input in enumerate(self.inputs):
            print(i, input)

        for i, output in enumerate(self.outputs):
            print(i, output)

    def __rshift__(self, other):
        """
        self >> other
        """
        return shift.rshift(self, other)

    def __rlshift__(self, other):
        """
        other << self
        """
        return shift.rshift(self, other)

    def __lshift__(self, other):
        """
        self << other
        """
        return shift.lshift(self, other)

    def __rrshift__(self, other):
        """
        other >> self
        """
        return shift.lshift(self, other)
