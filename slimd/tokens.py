from mistletoe.span_token import SpanToken
from mistletoe.block_token import BlockToken, CodeFence, ThematicBreak

import re
import shlex


class SlideBreak(ThematicBreak):
    pattern = re.compile(r' {0,3}(?:([-_+*])\s*?)(?:\1\s*?){2,}(.*)$')

    def __init__(self, lines):
        m = SlideBreak.pattern.match(lines[0]).group(1)
        self.props = {}
        if not m.strip():
            return
        for kv in m.split('&'):
            if '=' in kv:
                k, v = kv.split('=', 1)
            else:
                k, v = kv, ''
            self.props[k] = v


class AsideBlock(BlockToken):
    pattern = re.compile(r':::\s+(.*)$')

    def __init__(self, lines):
        header, *content = lines
        headline = AsideBlock.pattern.match(header).group(1)
        aside_type, *aside_params = shlex.split(headline, False)
        self.aside_content = content
        self.aside_type = aside_type
        self.aside_params = aside_params

    @classmethod
    def start(cls, line):
        return cls.pattern.match(line)

    @staticmethod
    def read(lines):
        res = [next(lines)]

        def _is_content(line: str):
            return (
                not line.strip()
                or line.startswith('    ')
                or line.startswith('\t')
            )

        while _is_content(lines.peek()):
            l = next(lines)
            if l.startswith('    '):
                l = l[4:]
            elif l.startswith('\t'):
                l = l[1:]
            res.append(l)

        return res

class BetterCodeFence(CodeFence):
    """
    Code fence. (["```sh\\n", "rm -rf /", ..., "```"])
    Boundary between span-level and block-level tokens.

    Attributes:
        children (list): contains a single span_token.RawText token.
        language (str): language of code block (default to empty).
    """
    pattern = re.compile(r'( {0,3})((?:`|~){3,}) *(\S*)\s+(.*)')
    def __init__(self, match):
        super().__init__(match)
        _, open_info = match
        self.params = open_info[3]

    @classmethod
    def start(cls, line):
        match_obj = cls.pattern.match(line)
        if not match_obj:
            return False
        prepend, leader, lang, params = match_obj.groups()
        if leader[0] in lang or leader[0] in line[match_obj.end():]:
            return False
        CodeFence._open_info = len(prepend), leader, lang, params
        return True