import config
import socket


class Strip:
    """
    The Strip class defines operations for a 1-dimensional string of leds.
    """
    rgb = []

    def __init__(self):
        """
        Constructor, creating a strip of length leds.
        """
        self.length = config.length
        self.alpha = config.fade
        self.clear()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.connect(config.address)

    def clear(self, color=(0, 0, 0)):
        """
        Clear the entire strip with one color (default: black).
        Color is array: [r, g, b].
        """
        self.rgb = [color for _i in range(self.length)]

    def set(self, index, color):
        """
        Set led at index to color.
        """
        self.rgb[index] = color

    def append(self, color):
        """
        Append a color to the end of the strip.
        """
        self.rgb = self.rgb[1:] + [color]

    def fade(self, a):
        """
        Fade that strip by a factor a
        """
        self.rgb = [(int(r * a), int(g * a), int(b * a))
                    for r, g, b in self.rgb]

    def send(self):
        """
        Send the strip to the server.
        """
        flat = [int(item) for sublist in self.rgb for item in sublist]
        self.socket.sendall(bytes(flat))
