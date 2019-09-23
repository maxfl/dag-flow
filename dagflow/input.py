from __future__ import print_function
from dagflow import tools
from dagflow.shift import rshift, lshift
from dagflow.edges import EdgeContainer

class Input(object):
    _name  = tools.undefinedname
    _node  = tools.undefinednode
    _output = tools.undefinedoutput
    _corresponding_output = tools.undefinedoutput

    def __init__(self, name, node, corresponding_output=tools.undefinedoutput):
        self._name = name
        self._node=node
        self._corresponding_output=corresponding_output

    def __str__(self):
        return '->| {name}'.format(name=self._name)

    def _set_output(self, output):
        if self._output:
            raise Exception('Output is already connected to the input')

        self._output = output

    def name(self):
        return self._name

    def tainted(self):
        return self._output.tainted()

    def data(self):
        return self._output.data()

    def touch(self):
        return self._output.touch()

    def datatype(self):
        return self._output.datatype()

    def corresponding_output(self):
        return self._corresponding_output

    def taint(self):
        self._node.taint()

    def output(self):
        return self._output

    def connected(self):
        return self._output

    def disconnected(self):
        return self._output is tools.undefinedoutput

    def node(self):
        return self._node

    def iter_inputs(self, disconnected_only=False):
        if disconnected_only and self.connected():
            return

        raise tools.StopNesting(self)

    def iter_corresponding_outputs(self):
        raise tools.StopNesting(self)

    __lshift__  = lshift
    __rrshift__ = lshift

class Inputs(EdgeContainer):
    _datatype = Input
    def __init__(self, iterable=None):
        EdgeContainer.__init__(self, iterable)

    def __str__(self):
        return '->[{}]|'.format(len(self))

    def iter_inputs(self, disconnected_only=False):
        for input in self:
            if disconnected_only and input.connected():
                continue

            yield input
