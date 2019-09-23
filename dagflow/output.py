from __future__ import print_function
from dagflow import tools
from dagflow.shift import rshift, lshift
from dagflow.edges import EdgeContainer

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

    def _connect_to(self, input):
        if input in self._inputs:
            raise Exception('Output is already connected to the input')

        self._inputs.append(input)
        input._set_output(self)

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

    def set_data(self, data):
        self._data = data
        self._datatype = type(data)
        return data

    def datatype(self):
        return self._datatype

    def connected(self):
        return bool(self._inputs)

    def disconnected(self):
        return not bool(self._inputs)

    def inputs(self):
        return self._inputs

    def node(self):
        return self._node

    def iter_outputs(self, disconnected_only=False):
        if disconnected_only and self.connected():
            return iter(tuple())

        raise tools.StopNesting(self)

    def iter_corresponding_outputs(self):
        raise tools.StopNesting(self)

class Outputs(EdgeContainer):
    _datatype = Output
    def __init__(self, iterable=None):
        EdgeContainer.__init__(self, iterable)

    def __str__(self):
        return '|[{}]->'.format(len(self))
