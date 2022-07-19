import time
import colorsys
from strip import Strip


class Lights:
    def __init__(self) -> None:
        self.strip = Strip()

    def run(self) -> None:
        hue = 0

        while True:
            hue += 1
            if hue > 360:
                hue = 0

            color = colorsys.hsv_to_rgb(hue / 360, 1, 1)
            color = tuple(int(c * 255) for c in color)

            for i in range(1, self.strip.length):
                self.strip.set(i, color)
            self.strip.send()

            time.sleep(.01)


if __name__ == "__main__":
    lights = Lights()
    lights.run()
