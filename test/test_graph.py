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

    # final.data()
    # d = GraphDot(g)
    # d.savegraph('output/test1/test_01.png')

test_01()
