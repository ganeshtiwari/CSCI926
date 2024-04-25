import pytest
from tools.funcs import timeit

def test_timeit(capsys):
    def func(x):
        return x
    timeit(1, func, 2)
    captured = capsys.readouterr()
    avg = float(captured.out.strip().split()[0])
    assert avg >= 0

