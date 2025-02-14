from sliding_window_decoder import *
import numpy as numpy

def test_generate_window_error_and_logical_ops():
    m = np.matrix([[1,1],[2,2]])
    logical_qubits = np.matrix([3,3])

    
    gen = generate_window_error_and_logical_ops(m, logical_qubits, stride=1, window_size=1, maxt=1)

    window, error, logical_ops = next(gen) 

    expected_window = np.matrix(([1,1,1,0], [2,2,0,1]))
    assert np.array_equal(expected_window, window)

    expecpted_logical_ops = np.matrix([3,3,0,0])
    assert np.array_equal(expecpted_logical_ops, logical_ops)

    assert (1, 4) == error.shape

    gen = generate_window_error_and_logical_ops(m, logical_qubits, stride=1, window_size=1, maxt=1)
