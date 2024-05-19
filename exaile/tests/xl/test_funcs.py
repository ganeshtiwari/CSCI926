import pytest
from tools.funcs import timeit

def test_timeit(capsys):
    def func(x):
        return x
    
    # n=0
    with pytest.raises(ValueError, match="'n' must be greater than 0"):
        timeit(0, func, 2)
    
    # n=-1
    with pytest.raises(ValueError, match="'n' must be greater than 0"):
        timeit(-1, func, 2)
    
    # n=1
    timeit(1, func, 2)
    captured = capsys.readouterr()
    avg = float(captured.out.strip().split()[0])
    assert avg >= 0
    
    # n=10
    timeit(10, func, 2)
    captured = capsys.readouterr()
    avg = float(captured.out.strip().split()[0])
    assert avg >= 0

