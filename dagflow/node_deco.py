from __future__ import print_function
from dagflow.node import Node
from dagflow.input_extra import MissingInputAddOne

def NodeClass(fcn=None, **kwargsdeco):
    if fcn:
        kwargsdeco['fcn'] = fcn
        class NewNodeClass(Node):
            def __init__(self, *args, **kwargsclass):
                self._fcn = fcn
                kwargs = dict(kwargsclass, **kwargsdeco)

                Node.__init__(self, *args, **kwargs)

        return NewNodeClass

    return lambda fcn1: NodeClass(fcn1, **kwargsdeco)

def NodeInstance(fcn=None, **kwargsinstance):
    if fcn:
        kwargsdeco=kwargsinstance.pop('class_kwargs', {})
        kwargsdeco.setdefault('name', fcn.__name__)
        cls=NodeClass(fcn, **kwargsdeco)
        return cls(**kwargsinstance)

    return lambda fcn1: NodeInstance(fcn1, **kwargsinstance)

def NodeInstanceStatic(fcn=None, **kwargsinstance):
    if fcn:
        kwargsdeco=kwargsinstance.pop('class_kwargs', {})
        kwargsdeco.setdefault('missing_input_handler', MissingInputAddOne())
        kwargsdeco.setdefault('name', fcn.__name__)
        def staticfcn(node, inputs, outputs):
            inputs._touch()
            return fcn()
        cls=NodeClass(staticfcn, **kwargsdeco)
        return cls(**kwargsinstance)

    return lambda fcn1: NodeInstanceStatic(fcn1, **kwargsinstance)
