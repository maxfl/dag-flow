#!/usr/bin/env python

from __future__ import print_function
from dagflow.node import NodeFunction
from dagflow.graph import Graph
from dagflow.graphviz import savegraph
import numpy as N
from dagflow.wrappers import *
from dagflow.printl import printl, set_prefix_function

set_prefix_function(lambda: '{:<2d} '.format(current_level()),)

def test_00():
    @NodeFunction
    def Array(self, inputs, outputs, node):
        if len(outputs):
            out = outputs[0]
        else:
            out = node._add_output('array')

        out.set_data(N.arange(5, dtype='d'))

    @NodeFunction
    def Adder(self, inputs, outputs, node):
        if not len(outputs):
            node._add_output('result')

        out = None
        for input in inputs:
            if out is None:
                out = outputs[0].set_data(input.data())
            else:
                out+=input.data()

    @NodeFunction
    def Multiplier(self, inputs, outputs, node):
        if not len(outputs):
            node._add_output('result')

        out = None
        for input in inputs:
            if out is None:
                out = outputs[0].set_data(input.data())
            else:
                out*=input.data()

    graph = Graph()
    in1 = graph.add_node('n1', nodeclass=Array)
    in2 = graph.add_node('n2', nodeclass=Array)
    in3 = graph.add_node('n3', nodeclass=Array)
    in4 = graph.add_node('n4', nodeclass=Array)
    s = graph.add_node('add', nodeclass=Adder)
    m = graph.add_node('mul', nodeclass=Multiplier)

    in1._add_output('array')
    in2._add_output('array')
    in3._add_output('array')
    in4._add_output('array')
    s._add_input(('i1', 'i2', 'i3'))
    s._add_output('result')
    m._add_input(('i1', 'i2'))
    m._add_output('result')

    (in1, in2, in3) >> s
    (in4, s) >> m

    graph._wrap_fcns(dataprinter, printer)

    result = m.outputs.result.data()
    printl(result)

    savegraph(graph, 'output/decorators_graph.pdf')

if __name__ == "__main__":
    test_00()

