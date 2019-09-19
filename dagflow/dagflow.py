from __future__ import print_function

from collections import OrderedDict
from tools import *
from input import Input
from output import Output
from node import Node

class Graph(object):
    _nodes  = None
    _inputs = None
    _outputs = None

    def __init__(self):
        self._nodes   = []
        self._inputs  = []
        self._outputs = []

    def add_node(self, name, fcn=lambda i, o, n: None, **kwargs):
        newnode = Node(name, fcn, self, **kwargs)
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

        label=nodedag.label() or nodedag.name()
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
