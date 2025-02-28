import numpy as np
from ldpc.bplsd_decoder import BpLsdDecoder
from gbstim import gb


def generate_window_error_and_logical_ops(
    parity_check,
    logical_ops,
    window_size: int = 5,
    stride: int = 2,
    error_rate: float = 0.001,
    maxt: int | None = 100,
):
    m, n = np.matrix(parity_check).shape
    extended_parity_check = np.column_stack((parity_check, np.identity(m)))
    # print(extended_parity_check, "\n", extended_parity_check.shape, "\n")

    m_p, n_p = extended_parity_check.shape

    measurement_error_to_next_round = np.column_stack(
        (np.zeros((m, n)), np.identity(m))
    )
    m_er, n_er = measurement_error_to_next_round.shape
    # print(measurement_error_to_next_round, "\n", measurement_error_to_next_round.shape, "\n")

    measurement_round_check = np.column_stack(
        (measurement_error_to_next_round, extended_parity_check)
    )
    m_mr, n_mr = measurement_round_check.shape
    # print("____________")
    # print(measurement_round, measurement_round.shape)
    # print("____________")

    extended_logical_ops = np.column_stack(
        (logical_ops, np.zeros((logical_ops.shape[0], m)))
    )
    m_l, n_l = extended_logical_ops.shape

    print(m_p, n_p, "extended_parity_check")
    print(m_l, n_l, "extended_logical_ops")
    print(m_mr, n_mr, "measurement_round_check")

    cur_window = 1
    start_column = 0

    buffer_size = window_size - stride
    cell_columns = window_size * n_p
    while (maxt is not None and cur_window <= maxt) or maxt is None:
        window_columns = (
            cur_window * cell_columns
            if cur_window == 1
            else cur_window * cell_columns - buffer_size * n_p
        )
        print(f"{window_columns}")

        if cur_window > 1:
            start_column -= buffer_size * n_p

        start_row = 0

        window = np.zeros((window_size * m_p, window_columns))

        # print("____________")
        # print(window, window.shape)
        # print("____________")

        error_vec = np.random.binomial(1, error_rate, size=cell_columns).reshape(
            (1, cell_columns)
        )
        window_error_vec = np.zeros((1, window_columns), dtype=int)
        window_logical_ops = np.zeros((m_l, window_columns))

        # print(error_vec)
        # print(f"{window_error_vec.shape=}  {error_vec.shape=}")

        window_error_vec[:, -window_size * n_p :] = error_vec
        # print(window_error_vec)

        for i in range(0, window_size):
            if cur_window == 1 and i == 0:
                window[0:m_p, 0:n_p] = extended_parity_check
                window_logical_ops[:, 0:n_p] = extended_logical_ops
            else:
                window[
                    start_row : start_row + m_p, start_column : start_column + n_mr
                ] = measurement_round_check

                window_logical_ops[:, start_column + n_er : start_column + n_mr] = (
                    extended_logical_ops
                )
                start_column += n_p
            start_row += m_p

        cur_window += 1
        # print(window)
        # print("____________")

        yield window, window_error_vec, window_logical_ops


def sliding_window_decoder(
    code: gb.GBCode,
    window_size: int,
    stride: int,
    error_rate: float = 0.001,
    rounds: int | None = 100,
    verbose: bool = False,
):
    # window_size = 2*code.d # use double the code distance as the window size
    # stride = code # set the stride to the code distance

    gen_window = generate_window_error_and_logical_ops(
        code.Gz, code.Z, window_size, stride, error_rate, rounds
    )
    num_errors = 0
    previous_syndrome = None

    for i, output in enumerate(gen_window):
        window, error, logical_ops = output
        bp_lsd = BpLsdDecoder(
            window,
            error_rate=error_rate,
            bp_method="product_sum",
            max_iter=2,
            schedule="serial",
            lsd_method="lsd_cs",
            lsd_order=0,
        )

        syndrome = np.matrix(window) @ (error.T) % 2

        if previous_syndrome is not None:
            syndrome = previous_syndrome + syndrome

        lsd_decoding = bp_lsd.decode(syndrome)

        original_error = (logical_ops @ error.T) % 2
        lsd_error = (logical_ops @ lsd_decoding) % 2

        if verbose:
            print(f"\nShot {i}")
            print(f"Window: \t", window.shape)
            print(f"Syndrome: \t", syndrome.shape)
            print(f"Error: \t\t", original_error.shape)
            print(f"LSD Decoding: \t", lsd_error.shape)

        if not np.array_equal(original_error, lsd_error):
            num_errors += 1
            previous_syndrome = syndrome
            if verbose:
                print("LSD Decoding: Wrong")
        else:
            previous_syndrome = None

    if rounds:
        lsd_accuracy = (rounds - num_errors) / rounds
        print("lsd_accuracy = ", lsd_accuracy)
