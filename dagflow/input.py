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

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def node(self):
        return self._node

    @property
    def output(self):
        return self._output

    @property
    def corresponding_output(self):
        return self._corresponding_output

    @property
    def data(self):
        if not self._output:
            raise Exception('May not read data from disconnected input')
        return self._output.data

    @property
    def datatype(self):
        return self._output.datatype

    @property
    def tainted(self):
        return self._output.tainted

    def touch(self):
        return self._output.touch()

    def taint(self):
        self._node.taint()

    def connected(self):
        return bool(self._output)

    def disconnected(self):
        return not bool(self._output)

    def _deep_iter_inputs(self, disconnected_only=False):
        if disconnected_only and self.connected():
            return iter(tuple())

        raise tools.StopNesting(self)

    def _deep_iter_corresponding_outputs(self):
        if self._corresponding_output:
            raise tools.StopNesting(self._corresponding_output)

        return iter(tuple())

    __lshift__  = lshift
    __rrshift__ = lshift

class Inputs(EdgeContainer):
    _datatype = Input
    def __init__(self, iterable=None):
        EdgeContainer.__init__(self, iterable)

    def __str__(self):
        return '->[{}]|'.format(len(self))

    def _deep_iter_inputs(self, disconnected_only=False):
        for input in self:
            if disconnected_only and input.connected():
                continue

            yield input

    def _touch(self):
        for input in self:
            input.touch()

