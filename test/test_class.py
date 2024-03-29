#!/usr/bin/env python

from __future__ import print_function
from dagflow.node import FunctionNode
from dagflow.graph import Graph
from dagflow.graphviz import savegraph
from dagflow.input_extra import MissingInputAddOne
import numpy as N
from dagflow.wrappers import *

from dagflow.printl import printl, set_prefix_function, current_level
set_prefix_function(lambda: '{:<2d} '.format(current_level()),)

class Array(FunctionNode):
    """Creates a note with single data output with predefined array"""
    def __init__(self, name, array):
        FunctionNode.__init__(self, name)
        self._add_output('array')
        self.outputs.array.data = N.asanyarray(array)

class Adder(FunctionNode):
    """Adds all the inputs together"""
    def __init__(self, name):
        FunctionNode.__init__(self, name)
        self._missing_input_handler = MissingInputAddOne(output_fmt='result')

    @staticmethod
    def _fcn(node, inputs, outputs):
        if not len(inputs):
            return
        inputs = iter(inputs)
        ret = next(inputs).data.copy()
        for input in inputs:
            ret+=input.data

        outputs[0].data = ret

class Multiplier(FunctionNode):
    """Multiplies all the inputs together"""
    def __init__(self, name):
        FunctionNode.__init__(self, name)
        self._missing_input_handler = MissingInputAddOne(output_fmt='result')

    @staticmethod
    def _fcn(node, inputs, outputs):
        if not len(inputs):
            return
        inputs = iter(inputs)
        ret = next(inputs).data.copy()
        for input in inputs:
            ret*=input.data

        outputs[0].data = ret

def test_00():
    """Create four nodes: sum up three of them, multiply the result by the fourth
    Use graph context to create the graph.
    Use one-line code for connecting the nodes
    """
    array = N.arange(5)
    with Graph() as graph:
        initials = [Array(name, array) for name in ['n1', 'n2', 'n3', 'n4']]
        s = Adder('add')
        m = Multiplier('mul')

    (initials[3], (initials[:3] >> s)) >> m

    graph._wrap_fcns(dataprinter, printer)

    result = m.outputs.result.data
    printl(result)

    savegraph(graph, 'output/class_00.pdf')

if __name__ == "__main__":
    test_00()
