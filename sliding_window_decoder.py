import numpy as np
import ldpc.codes
from ldpc.bplsd_decoder import BpLsdDecoder
import ldpc
import qldpc
import galois
import matplotlib.pyplot as plt
from gbstim.device import Device
from gbstim import gb

def generate_window_and_error(parity_check, window_size: int = 5, error_rate=0.001, maxt=100):

    m, n = np.matrix(parity_check).shape
    extended_parity_check = np.column_stack((parity_check, np.identity(m)))
    print(extended_parity_check, "\n", extended_parity_check.shape, "\n")

    m1, n1 = extended_parity_check.shape

    measurement_error_to_next_round = np.column_stack((np.zeros((m, n)), np.identity(m)))
    print(measurement_error_to_next_round, "\n", measurement_error_to_next_round.shape, "\n")

    measurement_round = np.column_stack((measurement_error_to_next_round, extended_parity_check))
    print(measurement_round, "\n", measurement_round.shape, "\n")
    m2, n2 = measurement_round.shape

    print("____________")
    print(measurement_round, measurement_round.shape)
    print("____________")

    cur_window = 1
    start_column = 0
    while cur_window < maxt:
        start_row = 0

        window = np.zeros((window_size*m1, cur_window*window_size*n1))

        print("____________")
        print(window, window.shape)
        print("____________")

        error_vec = np.random.binomial(1, error_rate, size=window_size*n1).reshape((1,window_size*n1))
        print(error_vec)
        window_error_vec = np.zeros((1, cur_window*window_size*n1), dtype=int)
        print(f"{window_error_vec.shape=}  {error_vec.shape=}")

        window_error_vec[:, -window_size*n1:] = error_vec
        print(window_error_vec)

        for i in range(0, window_size):
            if cur_window == 1 and i == 0:
                window[0:m1, 0:n1] = extended_parity_check
            else:
                window[start_row: start_row+m1, start_column: start_column+n2] = measurement_round
                start_column += n1
            start_row += m1

        print(window)
        print("____________")



        cur_window+=1
        yield window, window_error_vec





    


def sliding_window_decoder(parity_check_martrix: np.ndarray, error_rate: float= 0.001, shots: int = 10000, verbose: bool = False):
    pass
