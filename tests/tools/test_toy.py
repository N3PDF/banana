# -*- coding: utf-8 -*-
from banana.tools import toy

pdf = toy.mkPDF("", 0)


def test_alpha():
    assert pdf.alphasQ(-1) == pdf.alphasQ2(-1) == 0.35


def test_set():
    assert pdf.set().name == "ToyLH"


def test_has_pid():
    assert pdf.hasFlavor(21)
    assert pdf.hasFlavor(0)
    assert pdf.hasFlavor(1)
    assert not pdf.hasFlavor(11)


def test_xf():
    for pid in [21, 1]:
        for Q2 in [-1, 10]:
            for x in [0.1, 0.2]:
                assert pdf.xfxQ2(pid, x, Q2) == pdf.xfxQ(pid, x, Q2)
            assert pdf.xfxQ2(pid, 2, Q2) == 0
