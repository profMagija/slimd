from io import StringIO
import os
import shlex
from typing import Union
from mistletoe import latex_token
from mistletoe.block_token import BlockCode, CodeFence, Document
from mistletoe.html_renderer import HTMLRenderer

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

from slimd.tokens import AsideBlock, BetterCodeFence, SlideBreak
from . import asides

RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'resources')

WRAPPER_START = '''
<!DOCTYPE html>
<html lang="en-001">
<head>
<meta charset="UTF-8">
<script type="text/javascript" id="MathJax-script" src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js">
</script>
<style>{}</style><style>{}</style><style>{}</style>'''.format(
    open(os.path.join(RESOURCES_DIR, 'style.css')).read(),
    open(os.path.join(RESOURCES_DIR, 'pygments.css')).read(),
    open(os.path.join(RESOURCES_DIR, 'default_theme.css')).read(),
)

WRAPPER_HEAD_END = '</head><body><div id="p">'

WRAPPER_END = '''</div><script>{}</script></body></html>'''.format(
    open(os.path.join(RESOURCES_DIR, 'script.js')).read(),
)


SLIDE_START_TEMPLATE = '''
<svg data-slimd-svg="" viewBox="0 0 {slide_w} {slide_h}" id="slide-{slide_id}">
<foreignObject width="{slide_w}" height="{slide_h}">
<section>
'''

SLIDE_END_TEMPLATE = '''
</section>
</foreignObject>
</svg>'''


def parse_code_block_opts(params):
    res = {}
    for param in shlex.split(params, False):
        if '=' not in param:
            k, v = param, ''
        else:
            k, v = param.split('=', 1)

        if k == 'number':
            res['linenos'] = 'table'
            if v:
                parts = v.split(',')
                if len(parts) >= 1 and parts[0]:
                    res['linenostart'] = int(parts[0])
                if len(parts) >= 2 and parts[1]:
                    res['linenostep'] = int(parts[1])
                if len(parts) >= 3 and parts[2]:
                    res['linenospecial'] = int(parts[2])
        elif k == 'highlight':
            hl = []
            for part in v.split(','):
                if not part:
                    continue
                if '-' in part:
                    start, end = part.split('-')
                else:
                    start, end = part, part
                start = int(start)
                end = int(end)
                if start > end:
                    end, start = start, end
                hl.extend(range(start, end+1))
            res['hl_lines'] = hl
    return res


class SlimdHtmlRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__(
            SlideBreak,
            AsideBlock,
            BetterCodeFence,
            latex_token.Math,
        )
        self.page_size = (1920, 1080)
        self.id = 1

    def _add_wrappers(self, content):
        return (
            WRAPPER_START
            + '<style>@page{{ size: {}px {}px; margin: 0px; }}</style>'.format(*self.page_size)
            + WRAPPER_HEAD_END
            + content
            + WRAPPER_END
        )

    def render_document(self, token: Document):
        return self._add_wrappers(
            SLIDE_START_TEMPLATE.format(
                slide_id=1,
                slide_w=self.page_size[0],
                slide_h=self.page_size[1],
            )
            + super().render_document(token)
            + '<script>const SLIMD_MAX_SLIDE = {};</script>'.format(self.id)
            + SLIDE_END_TEMPLATE
        )

    def render_slide_break(self, token):
        slide_id = self.id + 1
        self.id += 1
        return SLIDE_END_TEMPLATE + SLIDE_START_TEMPLATE.format(
            slide_id=slide_id,
            slide_w=self.page_size[0],
            slide_h=self.page_size[1],
        )

    def render_block_code(self, token: Union[BlockCode, CodeFence]):
        text = token.children[0].content
        if isinstance(token, CodeFence):
            opts = dict(wrapcode=True)

            if isinstance(token, BetterCodeFence):
                opts.update(parse_code_block_opts(token.params))
            try:
                lex = get_lexer_by_name(token.language)
                return highlight(text, lex, HtmlFormatter(**opts))
            except ClassNotFound:
                pass
        return '<div><pre>{}</pre></div>'.format(text)

    def render_aside_block(self, token: AsideBlock):
        if token.aside_type not in asides.HANDLERS:
            print(' Error: unknown aside:', token.aside_type)
            return ''
        handler = asides.HANDLERS[token.aside_type]
        return handler(''.join(token.aside_content), token.aside_params)

    def render_better_code_fence(self, token):
        return self.render_block_code(token)
    
    def render_math(self, token):
        token = token.content
        classes = 'katex'
        if token.startswith('$$'):
            text = token[2:-2]
            classes += ' katex-display'
        else:
            text = token[1:-1]
        
        return '<span class="{}">{}</span>'.format(
            classes,
            text
        )
