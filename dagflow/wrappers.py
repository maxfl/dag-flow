from __future__ import print_function
from dagflow.printl import printl, next_level

def printer(fcn, node, inputs, outputs):
    printl('Evaluate {node}'.format(node=node.name))
    with next_level():
        fcn(node, inputs, outputs)
    printl('... done with {node}'.format(node=node.name))

def before_printer(fcn, node, inputs, outputs):
    printl('Evaluate {node}: {label}'.format(node=node.name, label=node.label()))
    with next_level():
        fcn(node, inputs, outputs)

def after_printer(fcn, node, inputs, outputs):
    with next_level():
        fcn(node, inputs, outputs)
    printl('Evaluate {node}: {label}'.format(node=node.name, label=node.label()))

def dataprinter(fcn, node, inputs, outputs):
    fcn(node, inputs, outputs)
    for i, output in enumerate(outputs):
        printl('{: 2d} {}: {!s}'.format(i, output.name, output._data))

def toucher(fcn, node, inputs, outputs):
    for i, input in enumerate(inputs):
        printl('touch input {: 2d} {}.{}'.format(i, node.name, input.name))
        with next_level():
            input.touch()
    fcn(node, inputs, outputs)
