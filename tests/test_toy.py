from banana import toy
from scipy.integrate import quad

pdf = toy.mkPDF("", 0)
ff = toy.mkPDF("ToyFF_unpolarized", 0)


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


def test_toyFF():
    """Test the ToyFF_unpolarized with Eqn. 3.4 from 1501.00494."""

    val_u = round(quad(lambda x: ff.xfxQ2(2, x, 1), 0, 1)[0], 3)
    val_d = round(quad(lambda x: ff.xfxQ2(1, x, 1), 0, 1)[0], 3)
    val_g = round(quad(lambda x: ff.xfxQ2(21, x, 1), 0, 1)[0], 3)

    assert val_u == 0.401
    assert val_d == 0.094
    assert val_g == 0.238
