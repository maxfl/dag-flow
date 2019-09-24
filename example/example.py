#!/usr/bin/env python

from __future__ import print_function
from dagflow.node_deco import NodeClass
from dagflow.graph import Graph
from dagflow.graphviz import savegraph
from dagflow.input_extra import MissingInputAddOne
import numpy as N

# Node functions
@NodeClass(output='array')
def Array(node, inputs, outputs):
    """Creates a note with single data output with predefined array"""
    outputs[0].data = N.arange(5, dtype='d')

@NodeClass(missing_input_handler=MissingInputAddOne(output_fmt='result'))
def Adder(node, inputs, outputs):
    """Adds all the inputs together"""
    out = None
    for input in inputs:
        if out is None:
            out=outputs[0].data = input.data.copy()
        else:
            out+=input.data

@NodeClass(missing_input_handler=MissingInputAddOne(output_fmt='result'))
def Multiplier(node, inputs, outputs):
    """Multiplies all the inputs together"""
    out = None
    for input in inputs:
        if out is None:
            out = outputs[0].data = input.data.copy()
        else:
            out*=input.data

# The actual code
with Graph() as graph:
    (in1, in2, in3, in4) = [Array(name) for name in ['n1', 'n2', 'n3', 'n4']]
    s = Adder('add')
    m = Multiplier('mul')

(in1, in2, in3) >> s
(in4, s) >> m

print('Result is:', m.outputs.result.data)
savegraph(graph, 'example/dagflow_example.png')

