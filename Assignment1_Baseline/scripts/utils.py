import gzip

def fuzz_open(path, mode="r", isCompress=False):
    """
    Opens a file, transparently handling gzip-compressed logs.
    Reconstructed function: the original utils.py was not present in the
    public SQLiFuzz repo. This detects gzip magic bytes and falls back
    to a plain open() if the file isn't actually compressed.
    """
    if not isCompress:
        return open(path, mode)
    try:
        with open(path, 'rb') as test:
            magic = test.read(2)
        if magic == b'\x1f\x8b':
            return gzip.open(path, mode if 'b' in mode else mode + 't')
    except FileNotFoundError:
        raise
    return open(path, mode)
