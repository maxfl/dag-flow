#!/usr/bin/env python

from __future__ import print_function
from dagflow.node_deco import NodeClass, NodeInstance
from dagflow.graph import Graph
from dagflow.graphviz import savegraph
from dagflow.input_extra import MissingInputAddOne
import numpy as N
from dagflow.wrappers import *

from dagflow.printl import printl, set_prefix_function, current_level
set_prefix_function(lambda: '{:<2d} '.format(current_level()),)

@NodeClass(output='array')
def Array(self, inputs, outputs, node):
    outputs[0].set_data(N.arange(5, dtype='d'))

@NodeClass(missing_input_handler=MissingInputAddOne(output_fmt='result'))
def Adder(self, inputs, outputs, node):
    out = None
    for input in inputs:
        if out is None:
            out=outputs[0].set_data(input.data())
        else:
            out+=input.data()

@NodeClass(missing_input_handler=MissingInputAddOne(output_fmt='result'))
def Multiplier(self, inputs, outputs, node):
    out = None
    for input in inputs:
        if out is None:
            out = outputs[0].set_data(input.data())
        else:
            out*=input.data()

def test_00():
    graph = Graph()
    in1 = graph.add_node('n1', nodeclass=Array)
    in2 = graph.add_node('n2', nodeclass=Array)
    in3 = graph.add_node('n3', nodeclass=Array)
    in4 = graph.add_node('n4', nodeclass=Array)
    s = graph.add_node('add', nodeclass=Adder)
    m = graph.add_node('mul', nodeclass=Multiplier)

    (in1, in2, in3) >> s
    (in4, s) >> m

    graph._wrap_fcns(dataprinter, printer)

    result = m.outputs.result.data()
    printl(result)

    savegraph(graph, 'output/decorators_graph_00.pdf')

def test_01():
    with Graph() as graph:
        initials = [Array(name) for name in ['n1', 'n2', 'n3', 'n4']]
        s = Adder('add')
        m = Multiplier('mul')

    (initials[3], (initials[:3] >> s)) >> m

    graph._wrap_fcns(dataprinter, printer)

    result = m.outputs.result.data()
    printl(result)

    savegraph(graph, 'output/decorators_graph_01.pdf')

def test_02():
    with Graph() as graph:
        initials = [Array(name) for name in ['n1', 'n2', 'n3', 'n4']]

        @NodeInstance(name='add', class_kwargs=dict(missing_input_handler=MissingInputAddOne(output_fmt='result')))
        def s(self, inputs, outputs, node):
            out = None
            for input in inputs:
                if out is None:
                    out=outputs[0].set_data(input.data())
                else:
                    out+=input.data()

        @NodeInstance(name='mul', class_kwargs=dict(missing_input_handler=MissingInputAddOne(output_fmt='result')))
        def m(self, inputs, outputs, node):
            out = None
            for input in inputs:
                if out is None:
                    out = outputs[0].set_data(input.data())
                else:
                    out*=input.data()

    (initials[3], (initials[:3] >> s)) >> m

    graph._wrap_fcns(dataprinter, printer)

    result = m.outputs.result.data()
    printl(result)

    savegraph(graph, 'output/decorators_graph_02.pdf')

if __name__ == "__main__":
    test_00()
    test_01()
    test_02()

