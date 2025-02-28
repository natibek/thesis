import numpy as np
from ldpc.bplsd_decoder import BpLsdDecoder

class Window:
    def __init__(
            self, 
            parity_check, 
            logical_ops, 
            window_size: int, 
            stride: int, 
            error_rate: float,
    ):
        self.window_size = window_size
        self.error_rate = error_rate

        m, n = np.matrix(parity_check).shape

        self.extended_parity_check = np.column_stack((parity_check, np.identity(m)))
        self.m_p, self.n_p = self.extended_parity_check.shape

        measurement_error_to_next_round = np.column_stack(
            (np.zeros((m, n)), np.identity(m))
        )
        self.m_er, self.n_er = measurement_error_to_next_round.shape

        self.measurement_round_check = np.column_stack(
            (measurement_error_to_next_round, self.extended_parity_check)
        )
        self.m_mr, self.n_mr = self.measurement_round_check.shape

        self.extended_logical_ops = np.column_stack(
            (logical_ops, np.zeros((logical_ops.shape[0], m)))
        )
        self.m_l, self.n_l = self.extended_logical_ops.shape

        self.buffer_size = (window_size - stride)*self.m_p
        self.commit_size = stride * self.m_p

        # number of columns in one window
        self.num_columns = (window_size + 1) * self.n_p 

        # the first window and its logical operators
        self.window_1 = np.zeros((self.window_size * self.m_p, self.num_columns))
        self.logical_ops_1 = np.zeros((self.m_l, self.num_columns))

        start_column = start_row = 0
        for i in range(0, self.window_size):
            if i == 0:
                self.window_1[0:self.m_p, 0:self.n_p] = self.extended_parity_check
                self.logical_ops_1[:, 0:self.n_p] = self.extended_logical_ops
            else:
                self.window_1[
                    start_row : start_row + self.m_p, start_column : start_column + self.n_mr
                ] = self.measurement_round_check

                self.logical_ops_1[:, start_column + self.n_er : start_column + self.n_mr] = (
                    self.extended_logical_ops
                )
                start_column += self.n_p
            start_row += self.m_p

        # decoder instance for the first window
        self.bp_lsd_1 = BpLsdDecoder(
            self.window_1,
            error_rate=self.error_rate,
            bp_method="product_sum",
            max_iter=2,
            schedule="serial",
            lsd_method="lsd_cs",
            lsd_order=0,
        )

        # all the other windows
        self.window_2 = np.zeros((self.window_size * self.m_p, self.num_columns))
        self.logical_ops_2= np.zeros((self.m_l, self.num_columns))

        start_column = start_row = 0
        for i in range(0, self.window_size):
            self.window_2[
                start_row : start_row + self.m_p, start_column : start_column + self.n_mr
            ] = self.measurement_round_check

            self.logical_ops_2[:, start_column + self.n_er : start_column + self.n_mr] = (
                self.extended_logical_ops
            )
            start_column += self.n_p
            start_row += self.m_p

        # decoder instance for the first window
        self.bp_lsd_2 = BpLsdDecoder(
            self.window_2,
            error_rate=self.error_rate,
            bp_method="product_sum",
            max_iter=2,
            schedule="serial",
            lsd_method="lsd_cs",
            lsd_order=0,
        )