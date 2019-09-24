#!/usr/bin/env python

from __future__ import print_function
from dagflow.node_deco import NodeInstanceStatic
from dagflow.graph import Graph
from dagflow.graphviz import savegraph
from dagflow.input_extra import MissingInputAddOne
import numpy as N
from dagflow.wrappers import *

from dagflow.printl import printl, set_prefix_function, current_level
set_prefix_function(lambda: '{:<2d} '.format(current_level()),)

with Graph() as graph:
    @NodeInstanceStatic(output='array')
    def array():
        printl('Call array')

    @NodeInstanceStatic()
    def adder():
        printl('Call Adder')

    @NodeInstanceStatic()
    def multiplier():
        printl('Call Multiplier')

def test_00():
    array >> adder
    (array, adder) >> multiplier

    graph._wrap_fcns(dataprinter, printer)

    result = multiplier.outputs[0].data
    printl(result)

    savegraph(graph, 'output/decorators_static_graph_00.pdf')

if __name__ == "__main__":
    test_00()

