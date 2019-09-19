from __future__ import print_function
from dagflow.printl import printl, next_level

def printer(fcn, inputs, outputs, node):
    printl('Evaluate {node}'.format(node=node.name()))
    with next_level():
        fcn(inputs, outputs, node)
    printl('... done with {node}'.format(node=node.name()))

def dataprinter(fcn, inputs, outputs, node):
    fcn(inputs, outputs, node)
    for i, output in enumerate(outputs):
        printl('{: 2d} {}: {!s}'.format(i, output.name(), output._data))

def toucher(fcn, inputs, outputs, node):
    for i, input in enumerate(inputs):
        printl('touch input {: 2d} {}.{}'.format(i, node.name(), input.name()))
        with next_level():
            input.touch()
    fcn(inputs, outputs, node)
