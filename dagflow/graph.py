from __future__ import print_function
from dagflow.node import Node

class Graph(object):
    _nodes  = None
    _inputs = None
    _outputs = None

    def __init__(self):
        self._nodes   = []
        self._inputs  = []
        self._outputs = []

    def add_node(self, name, **kwargs):
        NodeClass = kwargs.pop('nodeclass', Node)
        newnode = NodeClass(name, graph=self, **kwargs)
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
