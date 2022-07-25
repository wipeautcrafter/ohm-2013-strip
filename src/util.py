import numpy as np
import time as time


def normalize(arr: list[float]):
    """
    Normalize an array between range [0 - 1].
    """

    np_arr = np.array(arr)
    return (np_arr - np.min(np_arr)) / np.ptp(np_arr)


class Timer:
    """
    A timer that maintains a constant FPS.
    """

    def __init__(self, fps: float):
        self.frame_time = 1.0 / fps
        self.last_frame = time.time()

    def sleep(self):
        """
        Sleep until the next frame.
        """
        
        time.sleep(self.frame_time + self.last_frame - time.time())
        self.last_frame = time.time()