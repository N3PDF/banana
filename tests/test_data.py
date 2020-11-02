from banana import data

def test_power_set():
    inp = {
        "a": [1,2],
        "b": ["1", "2"]
    }
    out = data.power_set(inp)
    assert len(out) == 4
    assert len(list(filter(lambda e: e["a"] == 2,out))) == 2
