# -*- coding: utf-8 -*-

import pandas as pd
import rich
import rich.box
import rich.markdown
import rich.panel
from rich import style


class DFdict(dict):
    """
    Collects dataframes in a dictionary printing them along side.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msgs = []

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.__init__()

    def print(self, *msgs, sep=" ", end="\n", position=None):
        """
        Add new messages to the representation

        Parameters
        ----------
            msgs : str
                messages
            sep : str
                separator
            end : str
                end-of-line marker
        """
        buffer = []
        # usually an empty print only add an empty line
        if len(msgs) > 0:
            buffer.append(msgs[0])

            for msg in msgs[1:]:
                buffer.append(sep)
                buffer.append(msg)
        buffer.append(end)

        if position is None:
            position = len(self.msgs)

        self.msgs = self.msgs[:position] + buffer + self.msgs[position:]

    def __setitem__(self, key, value):
        self.print(key)
        self.print(value)
        self.print()
        super().__setitem__(key, value)

    def __repr__(self):
        return "".join([str(x) for x in self.msgs])

    def merge(self, other):
        merged = type(self)()

        for k in set(self.keys()) | set(other.keys()):
            if k not in other:
                merged[k] = self[k]
            elif k in other:
                merged[k] = pd.concat([self[k], other[k]])
            else:
                merged[k] = other[k]

        return merged

    @property
    def q2s(self):
        q2s = set()
        for df in self.values():
            q2s |= set(df["Q2"])
        return q2s

    def q2_slice(self, q2):
        sliced = type(self)()
        for k, v in self.items():
            sliced[k] = v[v["Q2"] == q2]
        return sliced

    def fancy(self, file=None):
        """
        Print on stdout... with style!

        Parameters
        ----------
        file : IO[str]
            File to write to, None for stdout (passed down to `rich`)
        """
        for msg in self.msgs:
            if isinstance(msg, str):
                if msg == "\n":
                    continue
                elif msg in self:
                    rich.print(file=file)
                    rich.print(
                        rich.panel.Panel.fit(
                            msg, style="magenta", box=rich.box.HORIZONTALS
                        ),
                        file=file,
                    )
                else:
                    rich.print(rich.markdown.Markdown(msg), file=file)
            else:
                rich.print(msg, file=file)

    def to_document(self):
        """
        Convert dataframes back to a true dictionary

        Returns
        -------
            d : dict
                raw dictionary
        """
        d = {}
        for k, v in self.items():
            d[k] = v.to_dict(orient="records")

        d["__msgs__"] = self.msgs

        return d

    @classmethod
    def from_document(cls, d):
        """
        Load dataframes from a previous dictionary dump

        Parameters
        ----------
        d : dict
            raw dictionary, containing a dump of a DFdict object

        Returns
        -------
        DFdict
            the loaded DFdict
        """
        dfd = cls()
        for k, v in d.items():
            dfd[k] = pd.DataFrame(v)

        del dfd["__msgs__"]
        dfd.msgs = d["__msgs__"]

        return dfd
