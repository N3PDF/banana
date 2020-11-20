# -*- coding: utf-8 -*-
import pandas as pd
from banana.navigator import dfdict

class TestDFdict():
    def test_print(self):
        dfd = dfdict.DFdict()
        dfd["a"] = 1
        assert str(dfd) == "1\n\n"
        dfd.print("test")
        assert str(dfd) == "1\n\ntest\n"
        dfd.print("te", "st")
        assert str(dfd) == "1\n\ntest\nte st\n"

    def test_to_doc(self):
        dfd = dfdict.DFdict()
        d = {"a": [1]}
        df = pd.DataFrame.from_dict(d)
        dfd["test"] = df
        assert dfd.to_document() == {"test":[{"a": 1}]}

