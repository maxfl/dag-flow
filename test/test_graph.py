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
    label = None
    def plot(suffix=''):
        global counter
        d = GraphDot(g)
        newlabel = label and label+suffix or suffix
        if newlabel is not None:
            d.set_label(newlabel)
        d.savegraph('output/test3/test_{:03d}.png'.format(counter))
        counter+=1

    def plotter(fcn, inputs, outputs, node):
        plot('[start evaluating {}]'.format(node.name()))
        fcn(inputs, outputs, node)
        plot('[done evaluating {}]'.format(node.name()))

    A1 = g.add_node('A1')
    A2 = g.add_node('A2', label='{name}|frozen node')
    A3 = g.add_node('A3')
    B  = g.add_node('B')
    C1 = g.add_node('C1')
    C2 = g.add_node('C2')
    D  = g.add_node('D')
    E  = g.add_node('E')
    F  = g.add_node('F')
    H  = g.add_node('H')

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
    H._add_pair('i1', 'o1')
    _, other = F._add_pair('i1', 'o1')
    _, final = E._add_pair('i1', 'o1')

    (A1, A2, A3, D[:1]) >> B >> (E, H)
    ((C1, C2) >> D[:,1]) >> F

    g.print()

    label = 'Initial graph state.'
    plot()

    label = 'Read E...'
    plot()
    plot()
    plot()
    final.data()
    label = 'Done reading E.'
    plot()

    label = 'Taint D.'
    plot()
    plot()
    plot()
    D.taint()
    plot()
    label = 'Read F...'
    other.data()
    label = 'Done reading F.'
    plot()

    label = 'Read E...'
    plot()
    plot()
    plot()
    final.data()
    label = 'Done reading E.'
    plot()

    label = 'Taint A2.'
    plot()
    plot()
    plot()
    A2.taint()
    plot()
    label = 'Read E...'
    plot()
    final.data()
    label = 'Done reading E.'
    plot()

    label = 'Unfreeze A2 (tainted).'
    plot()
    plot()
    plot()
    A2.unfreeze()
    plot()
    label = 'Read E...'
    plot()
    final.data()
    label = 'Done reading E.'
    plot()

    label = 'Unfreeze A2 (not tainted).'
    plot()
    plot()
    plot()
    A2.unfreeze()
    plot()
    label = 'Read E...'
    plot()
    final.data()
    label = 'Done reading E.'
    plot()

if __name__ == "__main__":
    test_01()
    test_02()
    test_03()
