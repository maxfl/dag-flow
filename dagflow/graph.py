from __future__ import print_function
from dagflow.tools import undefinedgraph

class Graph(object):
    _nodes  = None
    _inputs = None
    _outputs = None
    _context_graph = undefinedgraph

    def __init__(self):
        self._nodes   = []
        self._inputs  = []
        self._outputs = []

    def add_node(self, name, **kwargs):
        from dagflow import node
        NodeClass = kwargs.pop('nodeclass', node.FunctionNode)
        newnode = NodeClass(name, graph=self, **kwargs)
        return newnode

    def register_node(self, node):
        self._nodes.append(node)

    def add_nodes(self, pairs, **kwargs):
        return (self.add_node(name, fcn, **kwargs) for name, fcn in pairs)

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

    @classmethod
    def current(cls):
        return cls._context_graph

    def __enter__(self):
        Graph._context_graph = self
        return self

    def __exit__(self, *args, **kwargs):
        Graph._context_graph = undefinedgraph
