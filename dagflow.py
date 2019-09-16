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
        return self._output is not undefinedoutput

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

    def iter_outputs(self):
        yield self

    def connected(self):
        return bool(self._inputs)

    def free(self):
        return not bool(self._inputs)

    def inputs(self):
        return self._inputs

    def node(self):
        return self._node

class Node(object):
    _name = undefinedname
    _inputs  = None
    _outputs = None
    _graph   = undefinedgraph
    _tainted = True
    _frozen  = False
    _frozen_tainted  = False
    _auto_freeze = False
    _evaluating = False
    _fcn     = None
    _fcn_chain = None

    def __init__(self, name, fcn=lambda i, o, n: None, graph=undefinedgraph):
        self._name = name
        self._fcn = fcn
        self._fcn_chain = []
        self._inputs = OrderedDict()
        self._outputs = OrderedDict()
        self._graph = graph

    def name(self):
        return self._name

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

    def inputs(self):
        return tuple(self._inputs.values())

    def outputs(self):
        return tuple(self._outputs.values())

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
        self._fcn(self._inputs, self._outputs, self)
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
        for input in nodedag.inputs():
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
        for output in nodedag.outputs():
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
                attr['arrowhead']='tee'

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
    for i, input in enumerate(inputs.values()):
        print('    touch input {: 2d} {}.{}'.format(i, node.name(), input.name()))
        input.touch()
    fcn(inputs, outputs, node)
