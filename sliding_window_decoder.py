from window import Window
import numpy as np

class SlidingWindow(Window):
    def __init__(
            self, 
            parity_check, 
            logical_ops, 
            window_size: int, 
            stride: int, 
            error_rate: float,
            verbose: bool = True
    ):
        super().__init__(
            parity_check,
            logical_ops,
            window_size,
            stride,
            error_rate,
        )

        self.verbose = verbose
        # error from the previous window
        self.prev_error: np.array | None = None

        # syndrome from the previous window
        self.prev_syndrome: np.array | None = None

        # check matrix from the previous window
        self.prev_H = None
        
        print(self.window_1, self.window_1.shape)
        print(self.logical_ops_1, self.logical_ops_1.shape)
        print(self.window_2, self.window_2.shape)
        print(self.logical_ops_2, self.logical_ops_2.shape)

        self.round = 0
        self.fail_count = 0
        self.first_fail = 0

    def reset_decoding(self):
        self.prev_error: np.array | None = None
        self.prev_syndrome: np.array | None = None
        self.prev_H = None
        self.round = 0
        self.first_fail = 0
        self.fail_count = 0

    def decode_round(self):
        error_vec = np.random.binomial(1, self.error_rate, size=self.num_columns)
        H = self.window_1 if self.round == 0 else self.window_2
        logical_ops = self.logical_ops_1 if self.round == 0 else self.logical_ops_2
        decoder = self.bp_lsd_1 if self.round == 0 else self.bp_lsd_2

        syndrome = (H @ error_vec) % 2
        temp = syndrome.copy()
        if self.round > 0 and self.buffer_size != 0:

            error_vec[:self.num_columns // 2] = self.prev_error[self.num_columns // 2:]
            syndrome[:self.commit_size] = (
                self.prev_syndrome[self.commit_size:] 
                + self.prev_H[self.commit_size:, :] @ self.prev_error
                ) % 2
            assert np.array_equal(syndrome[self.commit_size:], temp[self.commit_size:])


        lsd_decoding = decoder.decode(syndrome)

        original_error = (logical_ops @ error_vec.T) % 2
        lsd_error = (logical_ops @ lsd_decoding) % 2
        correct = np.array_equal(original_error, lsd_error)

        if not correct:
            print(temp)
            print(syndrome)
            print(self.prev_error)

        self.prev_syndrome = syndrome
        self.prev_error = lsd_decoding
        self.prev_H = H
        self.round += 1
        return correct

    def simulate(self, iters: float | None = 1_000_000):
        """Returns the first round failed on and the fail rate."""
        failed = False

        while (iters is None and not failed) or (iters is not None and self.round < iters):
            failed = not self.decode_round()
            
            if failed:
                self.fail_count += 1
                if self.first_fail == 0:
                    self.first_fail = self.round

            if self.round % 1000 == 0:
                print(f"ROUND {self.round} => {self.fail_count}/{self.round} errors")

        return self.first_fail, self.fail_count / self.round