from contextlib import contextmanager


# lets follow the same spirit
@contextmanager
def lhapdf_path(newdir):
    import lhapdf  # pylint: disable=import-error, import-outside-toplevel

    paths = lhapdf.paths()
    lhapdf.pathsPrepend(str(newdir))
    try:
        yield
    finally:
        lhapdf.setPaths(paths)
