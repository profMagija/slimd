import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt


class Entry:
    __single__ = ()
    __list__ = ()

    def __init__(self, state, parent):
        self.state = state
        self.parent = parent

    def process_begin(self, *args: str, **kwargs: str):
        pass

    def process_end(self, *args: str, **kwargs: str):
        pass

    def process_line(self, *args: str, **kwargs: str):
        cmd, *params = args
        cmd = cmd.lower()

        if cmd in self.__single__:
            setattr(self, cmd, params[0])
        elif cmd in self.__list__:
            setattr(self, cmd, params)
        elif hasattr(self, 'process_' + cmd):
            getattr(self, 'process_' + cmd)(*params, **kwargs)
        else:
            raise Exception('unknown command in ' + type(self) + ': ' + cmd)

    def _get(self, name, map=None):
        v = getattr(self, name, None)
        if v is not None and map is not None:
            v = map(v)
        return v

    def _get_all(self, *names, map=None):
        return {
            name: self._get(name, map=map) for name in names if hasattr(self, name)
        }


class BarChart(Entry):
    ci = 'sd'
    __single__ = 'x y hue capsize n_boot units orient color errwidth errcolor'.split()
    __list__ = 'order hue_order'.split()

    def process_ci(self, ci):
        if ci == 'off':
            self.ci = None
        elif ci == 'sd':
            self.ci = ci
        else:
            self.ci = float(ci)

    def process_palette(self, *values, name=None):
        if name:
            self.palette = name
        else:
            self.palette = values

    def process_dodge(self):
        self.dodge = True

    def process_end(self, *args: str, **kwargs: str):
        sns.barplot(
            **self._get_all(*'x y hue order hue_order units orient color palette dodge errcolor'.split()),
            **self._get_all('capsize', 'errwidth', map=float),
            **self._get_all('n_boot', map=int),
            ci=self.ci,
            data=self.state.cur_dataset.data,
        )


class DataEntry(Entry):
    def process_begin(self, name='', *, example=None, csv=None):
        self.name = name
        if example:
            self.data = sns.load_dataset(example)
        elif csv:
            self.data = pd.read_csv(csv)

    def process_end(self, *args: str, **kwargs: str):
        self.state.cur_dataset = self
        if self.name:
            self.state.datasets[self.name] = self
