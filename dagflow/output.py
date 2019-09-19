from __future__ import print_function
import tools
import input as Input
from shift import rshift, lshift
from edges import EdgeContainer

class Output(object):
    _name   = tools.undefinedname
    _node   = tools.undefinednode
    _inputs = None

    _data   = tools.undefineddata
    _datatype = tools.undefineddatatype

    def __init__(self, name, node):
        self._name = name
        self._node=node
        self._inputs=[]

    def __str__(self):
        return '|-> {name}'.format(name=self._name)

    def name(self):
        return self._name

    def connect_to(self, input):
        if not isinstance(input, Input.Input):
            raise exception('Bad input type')

        if input in self._inputs:
            raise ConnectException('Output is already connected to the input')

        self._inputs.append(input)
        input.set_output(self)

    __rshift__  = rshift
    __rlshift__ = lshift

    def tainted(self):
        return self._node.tainted()

    def taint(self):
        for input in self._inputs:
            input.taint()

    def touch(self):
        return self._node.touch()

    def data(self):
        self._node.touch()
        return self._data

    def datatype(self):
        return self._datatype

    def _iter_outputs(self):
        yield self

    def connected(self):
        return bool(self._inputs)

    def free(self):
        return not bool(self._inputs)

    def inputs(self):
        return self._inputs

    def node(self):
        return self._node

class Outputs(EdgeContainer):
    _datatype = Output
    def __init__(self, iterable=None):
        EdgeContainer.__init__(self, iterable)

    def __str__(self):
        return '|[{}]->'.format(len(self))
