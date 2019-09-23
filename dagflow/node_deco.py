from __future__ import print_function
from dagflow.node import Node

def NodeClass(fcn=None, **kwargsdeco):
    if fcn:
        class NewNodeClass(Node):
            _fcn = fcn
            def __init__(self, *args, **kwargsclass):
                kwargs = dict(kwargsclass, **kwargsdeco)
                if 'fcn' in kwargs:
                    raise Exception('May not define function for NodeClass')

                Node.__init__(self, *args, **kwargs)

        return NewNodeClass

    return lambda fcn1: NodeClass(fcn1, **kwargsdeco)

def NodeInstance(fcn=None, **kwargsinstance):
    if fcn:
        kwargsdeco=kwargsinstance.pop('class_kwargs', {})
        cls=NodeClass(fcn, **kwargsdeco)
        return cls(**kwargsinstance)

    return lambda fcn1: NodeInstance(fcn1, **kwargsinstance)
