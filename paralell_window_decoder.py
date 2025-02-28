from window import Window
import numpy as np
from threading import Lock, Thread

class Layer1_Window(Window):
    def __init__(
            self, 
            parity_check, 
            logical_ops, 
            window_size: int, 
            stride: int, 
            error_rate: float,
    ):
        super().__init__(
            parity_check,
            logical_ops,
            window_size,
            stride,
            error_rate,
        )

class Layer2_Window(Window):
    def __init__(
            self, 
            parity_check, 
            logical_ops, 
            window_size: int, 
            stride: int, 
            error_rate: float,
    ):
        super().__init__(
            parity_check,
            logical_ops,
            window_size,
            stride,
            error_rate,
        )

        # error from the previous window
        self.prev_error: np.array | None = None

        # syndrome from the previous window
        self.prev_syndrome: np.array | None = None

        # check matrix from the previous window
        self.prev_H = None

        # error from the previous window
        self.succ_error: np.array | None = None

        # syndrome from the next window
        self.succ_syndrome: np.array | None = None

        # check matrix from the next window
        self.succ_H = None

class ParallelWindow:
    def __init__(
            self, 
            parity_check, 
            logical_ops, 
            window_size: int, 
            stride: int, 
            error_rate: float,
            verbose: bool = False
    ):

        self.layer1_decoding_finished = {}
        self.finised_lock = Lock()

        self.round_layer1 = 0
        self.layer1_lock = Lock()

        self.round_layer2 = 0
        self.layer2_lock = Lock()


    def decode_layer1(self):
        """
        1. aquire lock, get round of layer 1, increment, release lock
        2. decode the window
        3. aquire finished lock, update layer1_decoding_finished with key round and the syndrome
        """
        self.layer1_lock.acquire()

        my_round = self.round_layer1
        self.round_layer1 += 1

        self.layer1_lock.release()

        



    def decode_layer2(self):
        """
        1. aquire lock, get round of layer 2, increment, release lock
        2. wait while checking if both previous and next windows are decoded from first layer
            a. while loop with a lock to check for the correct keys in the layer1_decoding_finished
        3. decode the window
        """
        pass
