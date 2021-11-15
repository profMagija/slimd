import subprocess
from base64 import b64encode

from mistletoe import HTMLRenderer
from mistletoe.block_token import Document

HANDLERS = {}


def quick_render(text):
    return HTMLRenderer().render(Document(text))


def aside_handler(langcode):
    def _wrapper(f):
        if langcode in HANDLERS:
            print(' == warning - overwriting existing handler for', langcode, '==')
        HANDLERS[langcode] = f
        return f
    return _wrapper


@aside_handler('dot')
def dot_handler(content, params):
    proc = subprocess.run(
        ['dot', '-Tsvg'], input=content.encode(), capture_output=True)
    if proc.returncode == 0:
        return '<img src="data:image/svg+xml;base64,{}">'.format(
            b64encode(proc.stdout).decode()
        )
    else:
        print('`dot` exitted with status code',
              proc.returncode, ':', proc.stderr)
        return '<strong><font color="red">{}</font></strong>'.format(proc.stderr.decode())


@aside_handler('footer')
def footer_handler(content, params):
    return '<footer>{}</footer>'.format(
        quick_render(content)
    )


@aside_handler('latex')
def latex_handler(content, params):
    classes = 'katex'
    if 'inline' not in params:
        classes += ' katex-display'

    return '<span class="{}">{}</span>'.format(
        classes,
        content
    )

@aside_handler('graph')
def graph_handler(content, params):
    from .extensions import graph
    return graph.graph_handle(content, params)