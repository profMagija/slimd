import os
import tempfile
import click
from .renderer import SlimdHtmlRenderer
from mistletoe import Document

from watchdog import observers, events
import time

from tempfile import mktemp
import subprocess


def convert_file(in_file: str, out_file: str):
    print('converting', in_file, '-->', out_file, '... ', end='')
    if out_file.endswith('.pdf'):
        pdf_out_file = out_file
        out_file = mktemp('.html')
    else:
        pdf_out_file = None
    with open(in_file) as inf, open(out_file, 'w') as outf:
        with SlimdHtmlRenderer() as renderer:
            res = renderer.render(Document(inf))
            print(res, file=outf)
    if pdf_out_file is not None:
        subprocess.call([
            'chromium',
            '--headless',
            '--print-to-pdf-no-header',
            '--no-margins',
            '--disable-gpu',
            '--run-all-compositor-stages-before-draw',
            '--virtual-time-budget=10000',
            '--print-to-pdf=' + pdf_out_file,
            'file://' + out_file
        ])
        os.remove(out_file)
    print('done')


class ConvFileHandler(events.FileSystemEventHandler):

    def __init__(self, in_file, out_file):
        self.target = in_file
        self.params = (in_file, out_file)

    def on_modified(self, event: events.FileModifiedEvent):
        if event.src_path == self.target:
            convert_file(*self.params)


@click.command()
@click.argument('in_file')
@click.argument('out_file')
@click.option('--watch', type=bool, is_flag=True)
def slimd(in_file, out_file, watch):
    convert_file(in_file, out_file)
    if watch:
        ob = observers.Observer()
        ob.schedule(ConvFileHandler(in_file, out_file), in_file)
        ob.start()
        try:
            while True:
                time.sleep(10000)
        except KeyboardInterrupt:
            ob.stop()
        ob.join()


slimd()
