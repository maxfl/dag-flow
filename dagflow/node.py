from __future__ import print_function
from dagflow import legs, input as Input, output as Output, tools, input_extra
from dagflow.tools import IsIterable

def NodeFunction(fcn=None, **kwargsdeco):
    if fcn:
        class NewNodeClass(Node):
            _fcn = fcn
            def __init__(self, *args, **kwargsclass):
                kwargs = dict(kwargsclass, **kwargsdeco)
                if 'fcn' in kwargs:
                    raise Exception('May not define function for NodeFunction')

                Node.__init__(self, *args, **kwargs)

        return NewNodeClass

    def readfunction(fcn1):
        return NodeFunction(fcn1, **kwargsdeco)

    return readfunction

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
    missing_input_handler = None

    def __init__(self, name, **kwargs):
        legs.Legs.__init__(self)
        self._name = name

        newfcn = kwargs.pop('fcn', None)
        if newfcn:
            self._fcn = newfcn

        self._fcn_chain = []
        self._graph = kwargs.pop('graph', tools.undefinedgraph)
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

        missing_input_handler = kwargs.pop('missing_input_handler', None)
        if missing_input_handler:
            if isinstance(missing_input_handler, str):
                self.missing_input_handler = getattr(input_extra, missing_input_handler)(self)
            elif isinstance(missing_input_handler, type):
                self.missing_input_handler = missing_input_handler(self)
            else:
                self.missing_input_handler = missing_input_handler
                self.missing_input_handler.node = self
        else:
            self.missing_input_handler = input_extra.MissingInputFail(self)

        if kwargs:
            raise Exception('Unparsed arguments')

    def name(self):
        return self._name

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
            raise Exception('Output {node}.{output} already exist'.format(node=self.name(), output=name))

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
        prev_fcn = self._fcn
        self._fcn_chain.append(prev_fcn)
        def wrapped_fcn(*args, **kwargs):
            wrap_fcn(prev_fcn, *args, **kwargs)

        self._fcn = wrapped_fcn

        if other_fcns:
            self._wrap_fcn(*other_fcns)

    def _unwrap_fcn(self):
        if not self._fcn_chain:
            raise Exception('Unable to unwrap bare function')
        self._fcn = self._fcn_chain.pop()

    def touch(self, force=False):
        if self._frozen:
            return

        if not self._tainted and not force:
            return

        self.eval()
        self._tainted = False
        if self._auto_freeze:
            self._frozen = True

    def eval(self):
        self._evaluating = True
        self._fcn(self.inputs, self.outputs, self)
        self._evaluating = False

    def tainted(self):
        return self._tainted

    def set_auto_freeze(self):
        self._auto_freeze = True

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

    def evaluating(self):
        return self._evaluating

    def frozen(self):
        return self._frozen

    def immediate(self):
        return self._immediate

    def frozen_tainted(self):
        return self._frozen_tainted

    def taint(self, force=False):
        if self._tainted and not force:
            return

        if self._frozen:
            self._frozen_tainted = True
            return

        self._tainted = True

        if self._immediate:
            self.touch()

        for output in self.outputs:
            output.taint()

    def __getitem__(self, key):
        if isinstance(key, (int, slice, str)):
            return self.outputs[key]

        ret = legs.Legs.__getitem__(self, key)
        ret.missing_input_handler = self.missing_input_handler
        return ret

    def print(self):
        print('Node {}: ->[{}],[{}]->'.format(self._name, len(self.inputs), len(self.outputs)))
        for i, input in enumerate(self.inputs):
            print('  ', i, input)

        for i, output in enumerate(self.outputs):
            print('  ', i, output)
