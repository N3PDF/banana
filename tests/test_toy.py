import numpy as np
from scipy.integrate import quad

from banana import toy

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


def test_toyFF():
    """Test the ToyFF_unpolarized with Eqn. 3.4 from 1501.00494."""
    ff = toy.mkPDF("ToyFF_unpolarized", 0)

    val_u = quad(lambda x: ff.xfxQ2(2, x, 1), 0, 1)[0]
    val_d = quad(lambda x: ff.xfxQ2(1, x, 1), 0, 1)[0]
    val_g = quad(lambda x: ff.xfxQ2(21, x, 1), 0, 1)[0]

    np.testing.assert_allclose(val_u, 0.401, atol=1e-4)
    np.testing.assert_allclose(val_d, 0.094, atol=1e-4)
    np.testing.assert_allclose(val_g, 0.238, atol=1e-4)
