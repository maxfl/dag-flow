from collections import OrderedDict

class Undefined(object):
    def __init__(self, what):
        self.what=what

    def __str__(self):
        return 'Undefined '+self.what

    def __repr__(self):
        return 'Undefined("{what}")'.format(what=self.what)

undefinedname = Undefined('name')
undefineddata = Undefined('data')
undefineddatatype = Undefined('datatype')
undefinednode = Undefined('node')
undefinedgraph = Undefined('graph')
undefinedoutput = Undefined('output')

def iter_inputs(inputs):
    if isinstance(inputs, Input):
        yield inputs
    else:
        if isinstance(inputs, (tuple, list)):
            iterable = inputs
        elif isinstance(inputs, OrderedDict):
            iterable = inputs.values()
        elif isinstance(inputs, Node):
            iterable = inputs.iter_inputs()
        else:
            raise Exception('Do not know how to iterate inputs')

        for input in iterable:
            yield input

def iter_outputs(outputs):
    if isinstance(outputs, Output):
        yield outputs
    else:
        if isinstance(outputs, (tuple, list)):
            iterable = outputs
        elif isinstance(outputs, OrderedDict):
            iterable = outputs.values()
        elif isinstance(outputs, Node):
            iterable = outputs.iter_outputs()
        else:
            raise Exception('Do not know how to iterate outputs')

        for output in iterable:
            yield output

def rshift(outputs, inputs):
    corresponding_outputs = tuple()
    for output, input in zip(iter_outputs(outputs), iter_inputs(inputs)):
        output.connect_to(input)
        corresponding_outputs += input.corresponding_output(),

    return corresponding_outputs

def lshift(inputs, outputs):
    return rshift(outputs, inputs)

class Input(object):
    _name  = undefinedname
    _node  = undefinednode
    _output = undefinedoutput
    _corresponding_output = undefinedoutput

    def __init__(self, name, node, corresponding_output=undefinedoutput):
        self._name = name
        self._node=node
        self._corresponding_output=corresponding_output

    def set_output(self, output):
        if not isinstance(output, Output):
            raise exception('Bad output type')

        if self._output is not undefinedoutput:
            raise ConnectException('Output is already connected to the input')

        self._output = output

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

    __lshift__  = lshift
    __rrshift__ = lshift

class Output(object):
    _name   = undefinedname
    _node   = undefinednode
    _inputs = None

    _data   = undefineddata
    _datatype = undefineddatatype

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

    def iter_outputs(self):
        yield self

class Node(object):
    _name = undefinedname
    _inputs  = None
    _outputs = None
    _graph   = undefinedgraph
    _tainted = True
    _fcn     = None
    _fcn_chain = None

    def __init__(self, name, fcn=lambda i, o, n: None, graph=undefinedgraph):
        self._name = name
        self._fcn = fcn
        self._fcn_chain = []
        self._inputs = OrderedDict()
        self._outputs = OrderedDict()
        self._graph = graph

    def _add_input(self, name, corresponding_output=undefinedoutput):
        if name in self._inputs:
            raise Exception('Input {node}.{input} already exist', node=self.name, input=name)
        input = Input(name, self, corresponding_output)
        self._inputs[name] = input

        if self._graph is not undefinedgraph:
            self._graph._add_input(input)

        return input

    def _add_output(self, name):
        if name in self._outputs:
            raise Exception('Output {node}.{output} already exist', node=self.name, output=name)

        output = Output(name, self)
        self._outputs[name] = output

        if self._graph is not undefinedgraph:
            self._graph._add_output(output)

        return output

    def _add_pair(self, iname, oname):
        output = self._add_output(oname)
        input = self._add_input(iname, output)
        return input, output

    def _wrap_fcn(self, wrap_fcn, *other_fcns):
        prev_fcn = self._fcn
        self._fcn_chain.append(prev_fcn)
        def wrapped_fcn(*args, **kwargs):
            wrap_fcn(prev_fcn, *args, **kwargs)

        self._fcn = wrapped_fcn

        if other_fcns:
            self._wrap_fcn(*other_fcns)

    def _unwrap_fcn(self):
        if not self._fcn_chain:
            raise Exception('Unable to unwrap bare function')
        self._fcn = self._fcn_chain.pop()

    def iter_outputs(self):
        for output in self._outputs.values():
            yield output

    def iter_inputs(self):
        for input in self._inputs.values():
            yield input

    def touch(self, force=False):
        if not self._tainted and not force:
            return

        self.eval()
        self._tainted = False

    def eval(self):
        self._fcn(self._inputs, self._outputs, self)

    def tainted(self):
        return self._tainted

    def taint(self):
        if self._tainted:
            return

        self._tainted = True

        for output in self._outputs.values():
            output.taint()

    __rshift__  = rshift
    __rlshift__ = rshift
    __lshift__  = lshift
    __rrshift__ = lshift

class Graph(object):
    _nodes  = None
    _inputs = None
    _outputs = None

    def __init__(self):
        self._nodes   = []
        self._inputs  = []
        self._outputs = []

    def add_node(self, name, fcn=lambda i, o, n: None):
        newnode = Node(name, fcn, self)
        self._nodes.append(newnode)
        return newnode

    def add_nodes(self, pairs):
        return (self.add_node(name, fcn) for name, fcn in pairs)

    def _add_input(self, input):
        self._inputs.append(input)

    def _add_output(self, output):
        self._outputs.append(output)

    def _wrap_fcns(self, *args):
        for node in self._nodes:
            node._wrap_fcn(*args)

    def _unwrap_fcns(self):
        for node in self._nodes:
            node._unwrap_fcn()

