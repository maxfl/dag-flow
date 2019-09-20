from __future__ import print_function

class MissingInputHandler(object):
    _node = None
    def __init__(self, node=None):
        self.node = node

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, node):
        self._node = node

    def __call__(self, idx=None, scope=None):
        pass

class MissingInputFail(MissingInputHandler):
    def __init__(self, node=None):
        MissingInputHandler.__init__(self, node)

    def __call__(self, idx=None, scope=None):
        raise Exception('Unable to iterate inputs further. No additional inputs may be created')

class MissingInputAdd(MissingInputHandler):
    input_fmt = 'input_{:02d}'
    def __init__(self, node=None, fmt=None):
        MissingInputHandler.__init__(self, node)
        if fmt is not None:
            self.input_fmt = fmt

    def __call__(self, idx=None, scope=None, **kwargs):
        if idx is None:
            idx = len(self.node.inputs)

        return self.node._add_input(self.input_fmt.format(idx), **kwargs)

class MissingInputAddPair(MissingInputAdd):
    output_fmt = 'output_{:02d}'
    def __init__(self, node=None, input_fmt=None, output_fmt=None):
        MissingInputAdd.__init__(self, node, input_fmt)

        if output_fmt is not None:
            self.output_fmt = output_fmt

    def __call__(self, idx=None, scope=None):
        idx_out = len(self.node.outputs)
        out = self.node._add_output(self.output_fmt.format(idx_out))

        return MissingInputAdd.__call__(self, idx, corresponding_output=out, scope=scope)

class MissingInputAddOne(MissingInputAdd):
    output_fmt = 'output_{:02d}'
    add_corresponding_output = False
    def __init__(self, node=None, input_fmt=None, output_fmt=None, add_corresponding_output=False):
        MissingInputAdd.__init__(self, node, input_fmt)

        if output_fmt is not None:
            self.output_fmt = output_fmt

        self.add_corresponding_output=add_corresponding_output

    def __call__(self, idx=None, scope=None):
        idx_out = len(self.node.outputs)
        if idx_out==0:
            out = self.node._add_output(self.output_fmt.format(idx_out))
        else:
            out = self.node.outputs[-1]

        if self.add_corresponding_output:
            return MissingInputAdd.__call__(self, idx, corresponding_output=out, scope=scope)

        return MissingInputAdd.__call__(self, idx, scope=scope)

class MissingInputAddEach(MissingInputAdd):
    output_fmt = 'output_{:02d}'
    add_corresponding_output = False
    scope = 0
    def __init__(self, node=None, input_fmt=None, output_fmt=None, add_corresponding_output=False):
        MissingInputAdd.__init__(self, node, input_fmt)

        if output_fmt is not None:
            self.output_fmt = output_fmt

        self.add_corresponding_output=add_corresponding_output

    def __call__(self, idx=None, scope=None):
        if scope==self.scope:
            out = self.node.outputs[-1]
        else:
            idx_out = len(self.node.outputs)
            out = self.node._add_output(self.output_fmt.format(idx_out))
            self.scope=scope

        if self.add_corresponding_output:
            return MissingInputAdd.__call__(self, idx, corresponding_output=out, scope=scope)

        return MissingInputAdd.__call__(self, idx, scope=scope)
