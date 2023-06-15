from banana import data


def test_cartesian_product():
    inp = {"a": [1, 2], "b": ["1", "2"]}
    out = data.cartesian_product(inp)
    assert len(out) == 4
    assert len(list(filter(lambda e: e["a"] == 2, out))) == 2
