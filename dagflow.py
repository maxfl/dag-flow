from __future__ import print_function

from collections import OrderedDict
from collections import Iterable
import itertools as I

def IsIterable(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, str)

def nth(iterable, n):
    "Returns the nth item or a default value"
    return next(I.islice(iterable, n, None))

class Undefined(object):
    def __init__(self, what):
        self.what=what

    def __str__(self):
        return 'Undefined '+self.what

    def __repr__(self):
        return 'Undefined("{what}")'.format(what=self.what)

    def __bool__(self):
        return False

undefinedname = Undefined('name')
undefineddata = Undefined('data')
undefineddatatype = Undefined('datatype')
undefinednode = Undefined('node')
undefinedgraph = Undefined('graph')
undefinedoutput = Undefined('output')
undefinedleg = Undefined('leg')

def iter_inputs(inputs):
    if isinstance(inputs, Input):
        yield inputs
    else:
        if isinstance(inputs, OrderedDict):
            iterable = inputs.values()
        elif IsIterable(inputs):
            iterable = inputs
        elif isinstance(inputs, Legs):
            iterable = inputs._iter_inputs()
        else:
            raise Exception('Do not know how to iterate inputs')

        for input in iterable:
            for input1 in iter_inputs(input):
                yield input1

def iter_outputs(outputs):
    if isinstance(outputs, Output):
        yield outputs
    else:
        if isinstance(outputs, OrderedDict):
            iterable = outputs.values()
        elif IsIterable(outputs):
            iterable = outputs
        elif isinstance(outputs, Legs):
            iterable = outputs._iter_outputs()
        else:
            raise Exception('Do not know how to iterate outputs')

        for output in iterable:
            for output1 in iter_outputs(output):
                yield output1

def iter_corresponding_outputs(inputs):
    if isinstance(inputs, Input):
        yield inputs.corresponding_output()
    elif isinstance(inputs, Output):
        yield inputs
    else:
        if isinstance(inputs, OrderedDict):
            iterable = inputs.values()
        elif IsIterable(inputs):
            iterable = inputs
        elif isinstance(inputs, Legs):
            yield inputs
            return
        else:
            raise Exception('Do not know how to iterate corresponding outputs')

        for output in iterable:
            for output1 in iter_corresponding_outputs(output):
                yield output1

def rshift(outputs, inputs):
    corresponding_outputs = tuple(iter_corresponding_outputs(inputs))
    for output, input in I.zip_longest(iter_outputs(outputs), iter_inputs(inputs), fillvalue=undefinedleg):
        if output is undefinedleg or input is undefinedleg:
            raise Exception('Unable to connect mismatching lists')

        output.connect_to(input)

    if len(corresponding_outputs)==1:
        return corresponding_outputs[0]
    return corresponding_outputs

def lshift(inputs, outputs):
    return rshift(outputs, inputs)

class EdgeContainer(object):
    _dict = None
    _datatype = None
    def __init__(self, iterable=None):
        object.__init__(self)
        self._dict = OrderedDict()

        if iterable:
            self.__iadd__(iterable)

    def __iadd__(self, value):
        if IsIterable(value):
            for v in value:
                self.__iadd__(v)
            return self

        if self._datatype and not isinstance(value, self._datatype):
            raise Exception('The container does not support this type of data')

        name = value.name()
        if not name:
            raise Exception('May not add objects with undefined name')

        if name in self._dict:
            raise Exception('May not add duplicated items')

        self._dict[name] = value

        return self

    def __getitem__(self, key):
        if isinstance(key, int):
            return nth(self._dict.values(), key)
        elif isinstance(key, str):
            return self._dict[key]
        elif isinstance(key, slice):
            return tuple(self._dict.values())[key]
        elif isinstance(key, Iterable):
            return tuple(self.__getitem__(k) for k in key)

        raise Exception('Unsupported key type: '+type(key).__name__)

    def __getattr__(self, name):
        return self._dict[name]

    def __len__(self):
        return len(self._dict)

    def __dir__(self):
        return self._dict.keys()

    def __iter__(self):
        return iter(self._dict.values())

    def __contains__(self, name):
        return name in self._dict

class Input(object):
    _name  = undefinedname
    _node  = undefinednode
    _output = undefinedoutput
    _corresponding_output = undefinedoutput

    def __init__(self, name, node, corresponding_output=undefinedoutput):
        self._name = name
        self._node=node
        self._corresponding_output=corresponding_output

    def __str__(self):
        return '->| {name}'.format(name=self._name)

    def set_output(self, output):
        if not isinstance(output, Output):
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
        return self._output is undefinedoutput

    def node(self):
        return self._node

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

    def __str__(self):
        return '|-> {name}'.format(name=self._name)

    def name(self):
        return self._name

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

class Inputs(EdgeContainer):
    _datatype = Input
    def __init__(self, iterable=None):
        EdgeContainer.__init__(self, iterable)

    def __str__(self):
        return '->[{}]|'.format(len(self))

class Outputs(EdgeContainer):
    _datatype = Output
    def __init__(self, iterable=None):
        EdgeContainer.__init__(self, iterable)

    def __str__(self):
        return '|[{}]->'.format(len(self))

class Legs(object):
    def __init__(self, inputs=None, outputs=None):
        object.__init__(self)

        self.inputs = Inputs(inputs)
        self.outputs = Outputs(outputs)

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

    __rshift__  = rshift
    __rlshift__ = rshift
    __lshift__  = lshift
    __rrshift__ = lshift


class Node(Legs):
    _name = undefinedname
    _graph   = undefinedgraph
    _tainted = True
    _frozen  = False
    _frozen_tainted  = False
    _auto_freeze = False
    _evaluating = False
    _fcn     = None
    _fcn_chain = None

    def __init__(self, name, fcn=lambda i, o, n: None, graph=undefinedgraph):
        Legs.__init__(self)
        self._name = name
        self._fcn = fcn
        self._fcn_chain = []
        self._graph = graph

    def name(self):
        return self._name

    def _add_input(self, name, corresponding_output=undefinedoutput):
        if IsIterable(name):
            return tuple(self._add_output(n) for n in name)

        if name in self.inputs:
            raise Exception('Input {node}.{input} already exist', node=self.name, input=name)
        input = Input(name, self, corresponding_output)
        self.inputs += input

        if self._graph:
            self._graph._add_input(input)

        return input

    def _add_output(self, name):
        if IsIterable(name):
            return tuple(self._add_output(n) for n in name)

        if name in self.outputs:
            raise Exception('Output {node}.{output} already exist', node=self.name, output=name)

        output = Output(name, self)
        self.outputs += output

        if self._graph:
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

    def touch(self, force=False):
        if self._frozen:
            return

        if not self._tainted and not force:
            return

        self.eval()
        self._tainted = False
        if self._auto_freeze:
            self._frozen = True

    def eval(self):
        self._evaluating = True
        self._fcn(self.inputs, self.outputs, self)
        self._evaluating = False

    def tainted(self):
        return self._tainted

    def set_auto_freeze(self):
        self._auto_freeze = True

    def freeze(self):
        if self._frozen:
            return

        if self._tainted:
            raise Exception('Unable to freeze tainted node')

        self._frozen = True
        self._frozen_tainted = False

    def unfreeze(self):
        if not self._frozen:
            return

        self._frozen = False

        if self._frozen_tainted:
            self._frozen_tainted = False
            self.taint(force=True)

    def evaluating(self):
        return self._evaluating

    def frozen(self):
        return self._frozen

    def frozen_tainted(self):
        return self._frozen_tainted

    def taint(self, force=False):
        if self._tainted and not force:
            return

        if self._frozen:
            self._frozen_tainted = True
            return

        self._tainted = True

        for output in self.outputs:
            output.taint()

    def __getitem__(self, key):
        if isinstance(key, (int, slice, str)):
            return self.outputs[key]

        return Legs.__getitem__(self, key)

    def print(self):
        print('Node {}: ->[{}],[{}]->'.format(self._name, len(self.inputs), len(self.outputs)))
        for i, input in enumerate(self.inputs):
            print('  ', i, input)

        for i, output in enumerate(self.outputs):
            print('  ', i, output)

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

    def print(self):
        print('Graph with {} nodes'.format(len(self._nodes)))
        for node in self._nodes:
            node.print()

class GraphDot(object):
    _graph = None
    def __init__(self, dag, **kwargs):
        kwargs.setdefault('fontsize', 10)
        kwargs.setdefault('labelfontsize', 10)
        kwargs.setdefault('rankdir', 'LR')

        self._nodes = OrderedDict()
        self._nodes_open_input = OrderedDict()
        self._nodes_open_output = OrderedDict()
        self._edges = OrderedDict()

        import pygraphviz as G
        self._graph=G.AGraph(directed=True, strict=False,**kwargs)

        self._transform(dag)

    def _transform(self, dag):
        for nodedag in dag._nodes:
            self._add_node(nodedag)

        for nodedag in dag._nodes:
            self._add_open_inputs(nodedag)
            self._add_edges(nodedag)

        self.update_style()

    def get_id(self, object, suffix=''):
        return '{}_{!s}'.format(type(object).__name__, id(object))+suffix

    def _add_node(self, nodedag):
        styledict = dict(shape='Mrecord')

        label=nodedag.name()
        target=self.get_id(nodedag)
        self._graph.add_node(target, label=label, **styledict)
        nodedot = self._graph.get_node(target)

        self._nodes[nodedag] = nodedot

    def _add_open_inputs(self, nodedag):
        for input in nodedag.inputs:
            if input.connected():
                continue

            self._add_open_input(input, nodedag)

    def _add_open_input(self, input, nodedag):
        styledict = dict()

        source = self.get_id(input, '_in')
        target = self.get_id(nodedag)

        self._graph.add_node(source, shape='point', **styledict)
        self._graph.add_edge(source, target, **styledict)
        nodein  = self._graph.get_node(source)
        edge    = self._graph.get_edge(source, target)
        nodeout = self._graph.get_node(target)

        self._nodes_open_input[input] = nodein
        self._edges[input] = (nodein, edge, nodeout)

    def _add_edges(self, nodedag):
        for output in nodedag.outputs:
            if output.connected():
                for input in output.inputs():
                    self._add_edge(nodedag, output, input)
            else:
                self._add_open_output(nodedag, output)

    def _add_open_output(self, nodedag, output):
        styledict = dict()
        source = self.get_id(nodedag)
        target = self.get_id(output, '_out')

        self._graph.add_node(target, shape='point', **styledict)
        self._graph.add_edge(source, target, arrowhead='empty', **styledict)
        nodein  = self._graph.get_node(source)
        edge    = self._graph.get_edge(source, target)
        nodeout = self._graph.get_node(target)

        self._nodes_open_output[output]  = nodeout

        self._edges[output] = (nodein, edge, nodeout)

    def _add_edge(self, nodedag, output, input):
        styledict = dict()

        source = self.get_id(nodedag)
        target = self.get_id(input.node())
        self._graph.add_edge(source, target, **styledict)

        nodein  = self._graph.get_node(source)
        edge    = self._graph.get_edge(source, target)
        nodeout = self._graph.get_node(target)

        self._edges[input] = (nodein, edge, nodeout)

    def _set_style_node(self, node, attr):
        if not node:
            attr['color'] = 'gray'
        elif node.evaluating():
            attr['color'] = 'gold'
        elif node.tainted():
            attr['color'] = 'red'
        elif node.frozen_tainted():
            attr['color'] = 'blue'
        elif node.frozen():
            attr['color'] = 'cyan'
        else:
            attr['color'] = 'green'

    def _set_style_edge(self, obj, attrin, attr, attrout):
        if isinstance(obj, Input):
            if obj.connected():
                node = obj.output().node()
            else:
                node = None
                self._set_style_node(node, attrin)
        else:
            node = obj.node()
            self._set_style_node(node, attrout)

        self._set_style_node(node, attr)

        if node:
            if node.frozen():
                attrin['style']='dashed'
                attr['style']='dashed'
                # attr['arrowhead']='tee'
            else:
                attr['style']=''

    def update_style(self):
        for nodedag, nodedot in self._nodes.items():
            self._set_style_node(nodedag, nodedot.attr)

        for object, (nodein, edge, nodeout) in self._edges.items():
            self._set_style_edge(object, nodein.attr, edge.attr, nodeout.attr)

    def set_label(self, label):
        self._graph.graph_attr['label']=label

    def savegraph(self, fname, verbose=True):
        if verbose:
            print('Write output file:', fname)

        if fname.endswith('.dot'):
            self._graph.write(fname)
        else:
            self._graph.layout(prog='dot')
            self._graph.draw(fname)

def printer(fcn, inputs, outputs, node):
    print('Evaluate {node}'.format(node=node.name()))
    fcn(inputs, outputs, node)
    print('    ... done with {node}'.format(node=node.name()))

def toucher(fcn, inputs, outputs, node):
    for i, input in enumerate(inputs):
        print('    touch input {: 2d} {}.{}'.format(i, node.name(), input.name()))
        input.touch()
    fcn(inputs, outputs, node)
