from __future__ import print_function
from dagflow import tools
from dagflow.node_group import NodeGroup

class Graph(NodeGroup):
    _context_graph = tools.undefinedgraph
    _label         = tools.undefinedname

    def __init__(self, *args, **kwargs):
        NodeGroup.__init__(self, *args)
        self._label = kwargs.pop('label', tools.undefinedname)

        if kwargs:
            raise Exception('Unparsed arguments: {!s}'.format(kwargs))

    def add_node(self, name, **kwargs):
        from dagflow import node
        NodeClass = kwargs.pop('nodeclass', node.FunctionNode)
        newnode = NodeClass(name, graph=self, **kwargs)
        return newnode

    def label(self, *args, **kwargs):
        if self._label:
            return self._label.format(self._label, nodes=len(self._nodes))

    def add_nodes(self, pairs, **kwargs):
        return (self.add_node(name, fcn, **kwargs) for name, fcn in pairs)

    def _add_input(self, input):
        # self._inputs.append(input)
        pass

    def _add_output(self, output):
        # self._outputs.append(output)
        pass

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
        Graph._context_graph = tools.undefinedgraph
