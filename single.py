import sys
import time
from strip import Strip


class Lights:
    def __init__(self, color) -> None:
        self.strip = Strip()
        self.color = color

    def run(self) -> None:

        while True:
            for i in range(1, self.strip.length):
                self.strip.set(i, self.color)
            self.strip.send()

            time.sleep(.5)


if __name__ == "__main__":
    color = [int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])]
    lights = Lights(color)
    lights.run()
