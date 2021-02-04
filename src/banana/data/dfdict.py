# -*- coding: utf-8 -*-


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

    def print(self, *msgs, sep=" ", end="\n"):
        """
        Add new messages to the representation

        .. todo :: will likely be removed in the future

        Parameters
        ----------
            msgs : str
                messages
            sep : str
                separator
            end : str
                end-of-line marker
        """
        if len(msgs) > 0:
            self.msgs.append(msgs[0])

            for msg in msgs[1:]:
                self.msgs.append(sep)
                self.msgs.append(msg)
        self.msgs.append(end)

    # def __setitem__(self, key, value):
    #     self.print(key)
    #     self.print(value)
    #     self.print()
    #     super().__setitem__(key, value)

    # def __repr__(self):
    #    return "".join([str(x) for x in self.msgs])

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

        return d
