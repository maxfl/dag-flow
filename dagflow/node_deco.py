from __future__ import print_function
from dagflow.node import Node, StaticNode, MemberNode
from dagflow.input_extra import MissingInputAddOne

def NodeClass(fcn=None, **kwargsdeco):
    """Create a node class based on a function. The result is a class which
    should be instantiated in order to be used as node."""
    if fcn:
        kwargsdeco['fcn'] = fcn
        parent = kwargsdeco.pop('parent', Node)
        class NewNodeClass(parent):
            def __init__(self, *args, **kwargsclass):
                self._fcn = fcn
                kwargs = dict(kwargsclass, **kwargsdeco)

                Node.__init__(self, *args, **kwargs)

        return NewNodeClass

    return lambda fcn1: NodeClass(fcn1, **kwargsdeco)

def NodeInstance(fcn=None, **kwargsinstance):
    """Create a node class based on a function and immediately instantiate it.
    The result is a node class instance which may be used as node."""
    if fcn:
        kwargsclass=kwargsinstance.pop('class_kwargs', {})
        kwargsclass.setdefault('name', fcn.__name__)
        cls=NodeClass(fcn, **kwargsclass)
        return cls(**kwargsinstance)

    return lambda fcn1: NodeInstance(fcn1, **kwargsinstance)

def NodeInstanceStatic(fcn=None, **kwargsinstance):
    """Create a node class based on a function with empty signature and
    immediately instantiate it. The result is a node class instance which may
    be used as node.

    To be used to build a dependency chain of a functions which do not read
    inputs and do not write outputs, but rather refer to some common data."""

    kwargsinstance.setdefault('output', 'result')
    if fcn:
        kwargsclass=kwargsinstance.pop('class_kwargs', {})
        kwargsclass.setdefault('missing_input_handler', MissingInputAddOne())
        kwargsclass.setdefault('name', fcn.__name__)
        cls=NodeClass(fcn, parent=StaticNode, **kwargsclass)
        return cls(**kwargsinstance)

    return lambda fcn1: NodeInstanceStatic(fcn1, **kwargsinstance)

def NodeInstanceMember(fcn=None, **kwargsinstance):
    """Create a node class based on a class member function with empty signature and
    immediately instantiate it. The result is a node class instance which may
    be used as node.

    To be used to build a dependency chain of a functions which do not read
    inputs and do not write outputs, but rather refer to some common data."""

    kwargsinstance.setdefault('output', 'result')
    if fcn:
        kwargsclass=kwargsinstance.pop('class_kwargs', {})
        kwargsclass.setdefault('missing_input_handler', MissingInputAddOne())
        kwargsclass.setdefault('name', fcn.__name__)
        cls=NodeClass(fcn, parent=MemberNode, **kwargsclass)
        return cls(**kwargsinstance)

    return lambda fcn1: NodeInstanceMember(fcn1, **kwargsinstance)

def initialize_member_nodes(self):
    for key in dir(self):
        val = getattr(self, key)
        if isinstance(val, MemberNode):
            val.obj = self
