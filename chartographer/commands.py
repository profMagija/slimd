import argparse
from functools import wraps

from matplotlib import pyplot as plt

from . import charts
import shlex


BEGIN_TYPES = {
    'bar': charts.BarChart,
    'data': charts.DataEntry,
}


class ChartState:
    def __init__(self):
        self.graph_stack = []
        self.cur_dataset = None

    def process_lines(self, lines):
        cl = ''
        for line in lines:
            if not line.strip():
                continue
            cl += line.strip()
            if cl[-1] == '\\':
                continue
            else:
                data = shlex.split(cl, True)
                cl = ''
                if not data:
                    continue
                cmd, *params = data
                params_iter = iter(params)
                kwargs = {}
                args = []
                for arg in params_iter:
                    if arg[0] == '-' and len(arg) > 1 and arg[1].isalpha():
                        kwargs[arg[1:]] = next(params_iter)
                    else:
                        args.append(arg)
                self.process_line(cmd, *args, **kwargs)

    def process_line(self, cmd, *args, **kwargs):
        if cmd == 'begin':
            self.process_begin(*args, **kwargs)
        elif cmd == 'end':
            self.process_end(*args, **kwargs)
        elif self.current_graph:
            self.current_graph.process_line(cmd, *args, **kwargs)
        else:
            raise Exception(
                'unexpected command outside of begin...end: ' + cmd)

    @property
    def current_graph(self):
        return self.graph_stack[-1] if self.graph_stack else None

    def process_begin(self, typ, *args, **kwargs):
        if typ not in BEGIN_TYPES:
            raise Exception('unknown begin type: ' + typ)
        inst = BEGIN_TYPES[typ](self, self.current_graph)
        self.graph_stack.append(inst)
        inst.process_begin(*args, **kwargs)

    def process_end(self, *args, **kwargs):
        if not self.current_graph:
            raise Exception('unexpected end without begin')
        result = self.current_graph.process_end(*args, **kwargs)
        self.graph_stack.pop()
        if not self.graph_stack:
            self.handle_toplevel(result)

    def handle_toplevel(self, value):
        pass
