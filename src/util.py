import numpy as np


def normalize(arr: list[float]):
    """
    Normalize an array between range [0 - 1].
    """

    np_arr = np.array(arr)
    return (np_arr - np.min(np_arr)) / np.ptp(np_arr)