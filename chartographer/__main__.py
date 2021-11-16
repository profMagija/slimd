import sys
import shlex

from matplotlib import pyplot as plt
from .commands import ChartState

state = ChartState()
state.handle_toplevel = lambda x: plt.show()
state.process_lines(sys.stdin)