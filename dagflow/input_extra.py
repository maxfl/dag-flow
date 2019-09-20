from __future__ import print_function

class MissingInputHandler(object):
    def __init__(self, node):
        self._node = node

    def __call__(self, idx=None):
        pass

class MissingInputFail(MissingInputHandler):
    def __init__(self, node):
        MissingInputHandler.__init__(self, node)

    def __call__(self, idx=None):
        raise Exception('Unable to iterate inputs further. No additional inputs may be created')

class MissingInputAdd(MissingInputHandler):
    input_fmt = 'input_{:02d}'
    def __init__(self, node, fmt=None):
        MissingInputHandler.__init__(self, node)
        if fmt is not None:
            self.input_fmt = fmt

    def __call__(self, idx=None, **kwargs):
        if idx is None:
            idx = len(self._node.inputs)

        return self._node.add_input(self.input_fmt.format(idx), **kwargs)

class MissingInputAddPair(MissingInputAdd):
    output_fmt = 'output_{:02d}'
    def __init__(self, node, input_fmt=None, output_fmt=None):
        MissingInputAdd.__init__(self, node, input_fmt)

        if output_fmt is not None:
            self.output_fmt = output_fmt

    def __call__(self, idx=None):
        idx_out = len(self._node.outputs)
        out = self._node.add_output(self.output_fmt.format(idx))

        return MissingInputAdd.__call__(self, idx, corresponding_output=output)

class MissingInputAddOne(MissingInputAdd):
    output_fmt = 'output_{:02d}'
    add_corresponding_output = False
    def __init__(self, node, input_fmt=None, output_fmt=None, add_corresponding_output=False):
        MissingInputAdd.__init__(self, node, input_fmt)

        if output_fmt is not None:
            self.output_fmt = output_fmt

        self.add_corresponding_output=add_corresponding_output

    def __call__(self, idx=None):
        idx_out = len(self._node.outputs)
        if idx_out==0:
            out = self._node.add_output(self.output_fmt.format(idx))
        else:
            if add_corresponding_output:
                out = self._node.outputs[-1]
            else:
                out = None

        return MissingInputAdd.__call__(self, idx, corresponding_output=output)
