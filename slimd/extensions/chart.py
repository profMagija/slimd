import io
from matplotlib import pyplot as plt
from base64 import b64encode
import chartographer.commands as ch

STATE = ch.ChartState()

def chart_handle(content, params):
    STATE.process_lines(content.splitlines())
    buf = io.BytesIO()
    plt.savefig(buf, format='svg')
    plt.close()
    v = b64encode(buf.getvalue()).decode()
    return '<img src="data:image/svg+xml;base64,{}">'.format(v)