#!/usr/bin/env python

from dagflow import *

def test_01():
    g = Graph()
    n1 = g.add_node('node1')
    n2 = g.add_node('node2')
    n3 = g.add_node('node3')
    g._wrap_fcns(toucher, printer)

    in1, out1 = n1._add_pair('i1', 'o1')
    out2 = n1._add_output('o2')

    _, out3 = n2._add_pair('i1', 'o1')
    n2._add_input('i2')

    _, final = n3._add_pair('i1', 'o1')

    (out1, out2) >> n2
    out3 >> n3

    d = GraphDot(g)
    d.savegraph('output/test1/test_00.png')

def test_02():
    g = Graph()
    n1 = g.add_node('node1')
    n2 = g.add_node('node2')
    n3 = g.add_node('node3')
    g._wrap_fcns(toucher, printer)

    out1 = n1._add_output('o1')
    out2 = n1._add_output('o2')

    _, out3 = n2._add_pair('i1', 'o1')
    n2._add_input('i2')

    _, final = n3._add_pair('i1', 'o1')

    (out1, out2) >> n2
    out3 >> n3

    d = GraphDot(g)
    d.savegraph('output/test2/test_00.png')

    final.data()
    d.savegraph('output/test2/test_01.png')

counter = 0
def test_03():
    g = Graph()
    def plot():
        global counter
        d = GraphDot(g)
        d.savegraph('output/test3/test_{:03d}.png'.format(counter))
        counter+=1

    def plotter(fcn, inputs, outputs, node):
        plot()
        fcn(inputs, outputs, node)
        plot()

    A1 = g.add_node('A1')
    A2 = g.add_node('A2')
    A3 = g.add_node('A3')
    B  = g.add_node('B')
    C1 = g.add_node('C1')
    C2 = g.add_node('C2')
    D  = g.add_node('D')
    E  = g.add_node('E')
    F  = g.add_node('F')

    A2.set_auto_freeze()

    g._wrap_fcns(toucher, printer, plotter)

    A1._add_output('o1')
    A2._add_output('o1')
    A3._add_output('o1')
    B._add_pair('i1', 'o1')
    B._add_pair('i2', 'o2')
    B._add_input('i3')
    B._add_input('i4')
    C1._add_output('o1')
    C2._add_output('o1')
    D._add_pair('i1', 'o1')
    D._add_pair('i2', 'o2')
    _, other = F._add_pair('i1', 'o1')
    _, final = E._add_pair('i1', 'o1')

    (A1.outputs()[0], A2.outputs()[0], A3.outputs()[0], D.outputs()[0]) >> B
    (C1.outputs()[0], C2.outputs()[0]) >> D
    D.outputs()[1] >> F
    B >> E

    plot()

    final.data()
    plot()

    D.taint()
    plot()
    other.data()
    plot()

    final.data()
    plot()

    A2.taint()
    plot()
    final.data()
    plot()

test_01()
test_02()
test_03()
