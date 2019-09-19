from __future__ import print_function
import tools
import output as Output
from shift import rshift, lshift
from edges import EdgeContainer

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

    def set_output(self, output):
        if not isinstance(output, Output.Output):
            raise exception('Bad output type')

        if self._output:
            raise ConnectException('Output is already connected to the input')

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

    def free(self):
        return self._output is tools.undefinedoutput

    def node(self):
        return self._node

    __lshift__  = lshift
    __rrshift__ = lshift

class Inputs(EdgeContainer):
    _datatype = Input
    def __init__(self, iterable=None):
        EdgeContainer.__init__(self, iterable)

    def __str__(self):
        return '->[{}]|'.format(len(self))
