from __future__ import print_function
from dagflow.node import Node
from dagflow.tools import undefinedgraph
from dagflow.graph import Graph

class MemberNodesHolder(object):
    _graph = undefinedgraph
    def __init__(self, graph=None):
        if graph is True:
            self._graph = Graph()
        if graph:
            self._graph = graph

        for key in dir(self):
            val = getattr(self, key)
            if isinstance(val, MemberNode):
                val.obj=self
                val.graph=self._graph

class MemberNode(Node):
    """Function signature: fcn(self)"""
    _obj = None
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)

    def eval(self):
        self._evaluating = True
        self.inputs._touch()
        ret = self._fcn(self._obj)
        self._evaluating = False
        return ret

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, obj):
        self._obj = obj

    def _stash_fcn(self):
        prev_fcn = self._fcn
        self._fcn_chain.append(prev_fcn)
        return lambda self1, inputs, outputs: prev_fcn(self1._obj)

    def _make_wrap(self, prev_fcn, wrap_fcn):
        def wrapped_fcn(self1):
            wrap_fcn(prev_fcn, self1, self1.inputs, self1.outputs)
        return wrapped_fcn

