from __future__ import print_function
from dagflow import legs, input as Input, output as Output, tools, input_extra
from dagflow.tools import IsIterable
from dagflow import graph

class Node(legs.Legs):
    _name           = tools.undefinedname
    _label          = tools.undefinedname
    _graph          = tools.undefinedgraph
    _fcn            = tools.undefinedfunction
    _fcn_chain      = None
    _tainted        = True
    _frozen         = False
    _frozen_tainted = False
    _auto_freeze    = False
    _evaluating     = False
    _immediate      = False

    def __init__(self, name, **kwargs):
        legs.Legs.__init__(self, missing_input_handler=kwargs.pop('missing_input_handler', None))
        self._name = name

        newfcn = kwargs.pop('fcn', None)
        if newfcn:
            self._fcn = newfcn

        self._fcn_chain = []
        self._graph = kwargs.pop('graph', graph.Graph.current())
        if self._graph:
            self._graph.register_node(self)
        self._label = kwargs.pop('label', tools.undefinedname)

        for opt in ('immediate', 'auto_freeze', 'frozen'):
            value = kwargs.pop(opt, None)
            if value is None:
                continue
            setattr(self, '_'+opt, bool(value))

        input = kwargs.pop('input', None)
        if input:
            self._add_input(input)

        output = kwargs.pop('output', None)
        if output:
            self._add_output(output)

        if kwargs:
            raise Exception('Unparsed arguments')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def tainted(self):
        return self._tainted

    @property
    def frozen_tainted(self):
        return self._frozen_tainted

    @property
    def frozen(self):
        return self._frozen

    @property
    def auto_freeze(self):
        return self._auto_freeze

    @auto_freeze.setter
    def auto_freeze(self, auto_freeze):
        self._auto_freeze = auto_freeze

    @property
    def evaluating(self):
        return self._evaluating

    @property
    def immediate(self):
        return self._immediate

    def label(self, *args, **kwargs):
        if self._label:
            kwargs.setdefault('name', self._name)
            return self._label.format(*args, **kwargs)

        return self._label

    def _add_input(self, name, corresponding_output=tools.undefinedoutput):
        if IsIterable(name):
            return tuple(self._add_input(n) for n in name)

        if name in self.inputs:
            raise Exception('Input {node}.{input} already exist'.format(node=self.name, input=name))
        input = Input.Input(name, self, corresponding_output)
        self.inputs += input

        if self._graph:
            self._graph._add_input(input)

        return input

    def _add_output(self, name):
        if IsIterable(name):
            return tuple(self._add_output(n) for n in name)

        if name in self.outputs:
            raise Exception('Output {node}.{output} already exist'.format(node=self.name, output=name))

        output = Output.Output(name, self)
        self.outputs += output

        if self._graph:
            self._graph._add_output(output)

        return output

    def _add_pair(self, iname, oname):
        output = self._add_output(oname)
        input = self._add_input(iname, output)
        return input, output

    def _wrap_fcn(self, wrap_fcn, *other_fcns):
        prev_fcn = self._stash_fcn()
        self._fcn = self._make_wrap(prev_fcn, wrap_fcn)

        if other_fcns:
            self._wrap_fcn(*other_fcns)

    def _unwrap_fcn(self):
        if not self._fcn_chain:
            raise Exception('Unable to unwrap bare function')
        self._fcn = self._fcn_chain.pop()

    def _stash_fcn(self):
        raise Exception('Unimplemented method: use FunctionNode, StaticNode or MemberNode')

    def _make_wrap(self, prev_fcn, wrap_fcn):
        raise Exception('Unimplemented method: use FunctionNode, StaticNode or MemberNode')

    def touch(self, force=False):
        if self._frozen:
            return

        if not self._tainted and not force:
            return

        ret = self.eval()
        self._tainted = False
        if self._auto_freeze:
            self._frozen = True

        return ret

    def eval(self):
        raise Exception('Unimplemented method: use FunctionNode, StaticNode or MemberNode')

    def freeze(self):
        if self._frozen:
            return

        if self._tainted:
            raise Exception('Unable to freeze tainted node')

        self._frozen = True
        self._frozen_tainted = False

    def unfreeze(self):
        if not self._frozen:
            return

        self._frozen = False

        if self._frozen_tainted:
            self._frozen_tainted = False
            self.taint(force=True)

    def taint(self, force=False):
        if self._tainted and not force:
            return

        if self._frozen:
            self._frozen_tainted = True
            return

        self._tainted = True

        if self._immediate:
            ret = self.touch()
        else:
            ret = None

        for output in self.outputs:
            output.taint()

        return ret

    def print(self):
        print('Node {}: ->[{}],[{}]->'.format(self._name, len(self.inputs), len(self.outputs)))
        for i, input in enumerate(self.inputs):
            print('  ', i, input)

        for i, output in enumerate(self.outputs):
            print('  ', i, output)

class FunctionNode(Node):
    """Function signature: fcn(node, inputs, outputs)

    Note: _fcn should be a static function with signature (node, inputs, outputs)

    - Function defined as instance property will become a static method:
        class Node(...):
            def __init__(self):
                self._fcn = ...
        node = Node()
        node.fcn() # will have NO self provided as first argument

    - Fucntion defined in a nested class with staticmethod:
        class Other(Node
            @staticmethod
            def _fcn():
                ...

        node = Node()
        node.fcn() # will have NO self provided as first argument

    - [deprecated] Function defined as class property will become a bound method:
        class Node(...):
            _fcn = ...
        node = Node()
        node.fcn() # will have self provided as first argument

    - [deprecated] Function defined via staticmethod decorator as class property will become a static method:
        class Node(...):
            _fcn = staticmethod(...)
        node = Node()
        node.fcn() # will have NO self provided as first argument
    """

    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)

    def _stash_fcn(self):
        self._fcn_chain.append(self._fcn)
        return self._fcn

    def _make_wrap(self, prev_fcn, wrap_fcn):
        def wrapped_fcn(node, inputs, outputs):
            wrap_fcn(prev_fcn, node, inputs, outputs)
        return wrapped_fcn

    def eval(self):
        self._evaluating = True
        ret = self._fcn(self, self.inputs, self.outputs)
        self._evaluating = False
        return ret

class StaticNode(Node):
    """Function signature: fcn()"""
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)

    def eval(self):
        self._evaluating = True
        self.inputs._touch()
        ret = self._fcn()
        self._evaluating = False
        return ret

    def _stash_fcn(self):
        prev_fcn = self._fcn
        self._fcn_chain.append(prev_fcn)
        return lambda node, inputs, outputs: prev_fcn()

    def _make_wrap(self, prev_fcn, wrap_fcn):
        def wrapped_fcn():
            wrap_fcn(prev_fcn, self, self.inputs, self.outputs)
        return wrapped_fcn

class MemberNode(Node):
    """Function signature: fcn(self)"""
    _obj = None
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)

    def eval(self):
        self._evaluating = True
        self.inputs._touch()
        ret = self._fcn(self._obj)
        self._evaluating = False
        return ret

    @property
    def obj(self):
        return self._obj

    @obj.setter
    def obj(self, obj):
        self._obj = obj

    def _stash_fcn(self):
        prev_fcn = self._fcn
        self._fcn_chain.append(prev_fcn)
        return lambda self1, inputs, outputs: prev_fcn(self1._obj)

    def _make_wrap(self, prev_fcn, wrap_fcn):
        def wrapped_fcn(self1):
            wrap_fcn(prev_fcn, self1, self1.inputs, self1.outputs)
        return wrapped_fcn

