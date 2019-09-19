from __future__ import print_function

def printer(fcn, inputs, outputs, node):
    print('Evaluate {node}'.format(node=node.name()))
    fcn(inputs, outputs, node)
    print('    ... done with {node}'.format(node=node.name()))

def toucher(fcn, inputs, outputs, node):
    for i, input in enumerate(inputs):
        print('    touch input {: 2d} {}.{}'.format(i, node.name(), input.name()))
        input.touch()
    fcn(inputs, outputs, node)
