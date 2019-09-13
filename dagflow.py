class Input(object):
    _name  = '<undefined>'
    _node  = None
    _output = None
    _corresponding_output = None

    def __init__(self, name, node, corresponding_output=None):
        self._name = name
        self._node=node
        self._corresponding_output=corresponding_output

    def set_output(self, output):
        if not isinstance(output, Output):
            raise exception('Bad output type')

        if self._output:
            raise ConnectException('Output is already connected to the input')

        self._output = output

    def tainted(self):
        return self._output.tainted()

    def data(self):
        return self._output.data()

    def datatype(self):
        return self._output.datatype()

    def corresponding_output(self):
        return self._corresponding_output

class Output(object):
    _name   = '<undefined>'
    _node  = None
    _inputs = None

    _data   = None
    _datatype = None

    def __init__(self, name, node):
        self._name = name
        self._node=node
        self._inputs=[]

    def connect_to(self, input):
        if not isinstance(input, Input):
            raise exception('Bad input type')

        if input in self._inputs:
            raise ConnectException('Output is already connected to the input')

        self._inputs.append(input)
        input.set_output(self)

    def __rshift__(self, input):
        self.connect_to(input)
        return input.corresponding_output()

    def __rlshift__(self, input):
        self.connect_to(input)
        return input.corresponding_output()

    def tainted(self):
        return self._node.tainted()

    def data(self):
        self._node.touch()
        return self._data

    def datatype(self):
        return self._datatype

from collections import OrderedDict
class Node(object):
    _name = '<undefined>'
    _inputs  = None
    _outputs = None
    _fcn     = None
    _graph   = None
    _tainted = true

    def __init__(self, name, fcn, graph=None):
        self._name = name
        self._fcn = fcn
        self._inputs = OrderedDict()
        self._outputs = OrderedDict()
        self._graph = graph

    def _add_input(name, corresponding_output=None):
        ret = Input(name, self, corresponding_output)
        self._inputs[name] = ret
        return ret

    def _add_output(name):
        ret = Output(name, self)
        self._output[name] = ret
        return ret

    def _add_pair(iname, oname):
        output = self._add_output(oname)
        input = self._add_input(iname, output)
        return input, output

    def touch(self):
        if not self._tainted:
            return

        self._fcn()

class Graph(object):
    _nodes  = None
    _inputs = None
    _outputs = None

    def __init__(self):
        self._nodes   = []
        self._inputs  = []
        self._outputs = []

    def add_node(self, name, fcn):
        newnode = Node(name, fcn, self)
        self._nodes.append(newnode)
        return newnode

