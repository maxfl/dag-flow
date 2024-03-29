from __future__ import print_function
from dagflow import tools
from dagflow.shift import rshift, lshift
from dagflow.edges import EdgeContainer
import itertools as I

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
    def inputs(self):
        return self._inputs

    @property
    def invalid(self):
        """Checks the validity of the current node"""
        return self._node.invalid

    @invalid.setter
    def invalid(self, invalid):
        """Sets the validity of the following nodes"""
        for input in self.inputs:
            input.invalid = invalid

    @property
    def data(self):
        self._node.touch()
        return self._data

    @data.setter
    def data(self, data):
        if self._datatype is tools.undefineddatatype:
            self._datatype = type(data)
        elif self._datatype!=type(data):
            raise Exception('Unable to change existing data type')

        self._data = data
        return data

    @property
    def datatype(self):
        return self._datatype

    @property
    def tainted(self):
        return self._node.tainted

    def _connect_to(self, input):
        if input in self._inputs:
            raise Exception('Output is already connected to the input')

        self._inputs.append(input)
        input._set_output(self)

    __rshift__  = rshift
    __rlshift__ = lshift

    def taint(self, force=False):
        for input in self._inputs:
            input.taint(force)

    def touch(self):
        return self._node.touch()

    def connected(self):
        return bool(self._inputs)

    def disconnected(self):
        return not bool(self._inputs)

    def _deep_iter_outputs(self, disconnected_only=False):
        if disconnected_only and self.connected():
            return iter(tuple())

        raise tools.StopNesting(self)

    def _deep_iter_corresponding_outputs(self):
        raise tools.StopNesting(self)

    def repeat(self):
        return RepeatedOutput(self)

class RepeatedOutput(object):
    def __init__(self, output):
        self._output = output

    def __iter__(self):
        return I.cycle((self._output,))

    __rshift__  = rshift
    __rlshift__ = lshift

class Outputs(EdgeContainer):
    _datatype = Output
    def __init__(self, iterable=None):
        EdgeContainer.__init__(self, iterable)

    def __str__(self):
        return '|[{}]->'.format(len(self))
