import time
from strip import Strip


class Lights:
    def __init__(self) -> None:
        self.strip = Strip()
        self.width = 5
        self.on_color = [150, 0, 150]
        self.off_color = [0, 0, 0]

    def run(self) -> None:
        while True:
            for i in range(0, self.strip.length + self.width):
                if i < self.strip.length:
                    self.strip.set(i, self.on_color)
                if i > self.width:
                    self.strip.set(i - self.width, self.off_color)

                self.strip.send()
                time.sleep(.1)



if __name__ == "__main__":
    lights = Lights()
    lights.run()
