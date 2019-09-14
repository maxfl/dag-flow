#!/usr/bin/env python

from dagflow import *

def test_01():
    i = Input('input', None)
    o = Output('output', None)

    o >> i

def test_02():
    n1 = Node('node1')
    n2 = Node('node2')

    n1._add_output('o1')
    n1._add_output('o2')

    n2._add_input('i1')
    n2._add_input('i2')
    n2._add_output('o1')

    n1 >> n2

def test_03():
    n1 = Node('node1')
    n2 = Node('node2')

    out = n1._add_output('o1')

    n2._add_input('i1')
    n2._add_output('o1')

    out >> n2

def test_04():
    n1 = Node('node1')
    n2 = Node('node2')

    out = n1._add_output('o1')

    n2._add_pair('i1', 'o1')

    final = out >> n2

def test_05():
    n1 = Node('node1')
    n2 = Node('node2')

    out1 = n1._add_output('o1')
    out2 = n1._add_output('o2')

    _, final = n2._add_pair('i1', 'o1')
    n2._add_input('i2')

    (out1, out2) >> n2

def test_06():
    n1 = Node('node1')
    n2 = Node('node2')

    out1 = n1._add_output('o1')
    out2 = n1._add_output('o2')

    _, final = n2._add_pair('i1', 'o1')
    n2._add_input('i2')

    (out1, out2) >> n2

    print(final.data())

def test_07():
    def printer(fcn, inputs, outputs, node):
        print('Evaluate {node}'.format(node=node._name))
        fcn(inputs, outputs, node)
        print('    ... done')

    def toucher(fcn, inputs, outputs, node):
        for input in inputs.values():
            input.touch()

    n1 = Node('node1')
    n2 = Node('node2')

    n1._wrap_fcn(printer, toucher)
    n2._wrap_fcn(printer, toucher)

    out1 = n1._add_output('o1')
    out2 = n1._add_output('o2')

    _, final = n2._add_pair('i1', 'o1')
    n2._add_input('i2')

    (out1, out2) >> n2

    print(final.data())
    import IPython; IPython.embed()

test_01()
test_02()
test_03()
test_04()
test_05()
test_06()
test_07()
