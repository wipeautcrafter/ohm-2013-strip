import socket
import time
import signal
import sys
import select
import os
import config

def signal_handler(_signal, _frame):
  """
  Signal handler to kill the application
  Usage: signal.signal(signal.SIGINT, signal_handler)
  """
  #print('Bye ...')
  strip.stop()
  os.kill(os.getpid(), signal.SIGKILL)
  sys.exit(0)


class Artnet:
  """
  The Artnet class provides operation for sending and receiving data
  using the Artnet protocol.
  """
  sock = 0
  length = 170

  #                       01234567   8   9   a   b   c   d   e   f   10  11
  #                                  op-code protver seq phy universe len
  dataHeader = bytearray(
      b"Art-Net\x00\x00\x50\x00\x0e\x00\x00\x00\x00\x02\x00")
      # b"Art-Net\x00\x00\x50\x00\x0e\x00\x00\x00\x00\x00\x33")
  #                    01234567   8   9   a   b   c   d
  #                               op-code protver
  pollMsg = bytearray(b"Art-Net\x00\x00\x20\x00\x0e\x00\xff")

  def __init__(self):
    self.addr = config.address
    self.fade = config.fade
    self.local_host = config.local_host
    self.local_port = config.local_port

    # Create UDP socket
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    self.sock.bind((self.local_host, self.local_port))

  def close(self):
    """
    Shutdown the connection
    """
    self.clear()
    self.sock.close()

  def clear(self):
    """
    Clear the entire strip
    """
    data = self.dataHeader
    for _i in range(self.length):
      data += b"\x00\x00\x00"
    for _i, address in enumerate(self.addr):
      self.sock.sendto(data, address)

  def send(self, current_strip):
    """
    Send the data of a strip
    """
    data = bytearray(3*current_strip.length)
    for i in reversed(range(current_strip.length)):
      c = current_strip.get(current_strip.length - 1 - i)
      data[3*i+0] = int(c[0] * self.fade)
      data[3*i+1] = int(c[1] * self.fade)
      data[3*i+2] = int(c[2] * self.fade)
    for _i, address in enumerate(self.addr):
      self.sock.sendto(self.dataHeader + data, address)

  def poll(self):
    """
    Run poll for 5 seconds.
    """
    devices = []
    self.sock.setblocking(0)
    for _i, address in enumerate(self.addr):
      self.sock.sendto(self.pollMsg, address)
    print("=== Sent artnet poll ===")
    now = time.time()
    while (time.time() - now) < 5:
      ready = select.select([self.sock], [], [], 0.5)
      if ready[0]:
        rdata, raddr = self.sock.recvfrom(5000)
        if (rdata[8]) == 0x00 and (rdata[9]) == 0x20:
          print("received poll request from", raddr[0], "@", raddr[1])
          # officially this needs to be answered with a reply
        if (rdata[8]) == 0x00 and (rdata[9]) == 0x21:
          print("received poll reply from", raddr[0], "@", raddr[1])
          devices.append(raddr)
    self.sock.setblocking(1)
    return devices


strip = None


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
    self.clear()
    self.artnet = Artnet()

    signal.signal(signal.SIGINT, signal_handler)

    global strip
    strip = self

  def stop(self):
    """
    Stop this strip
    """
    if "globalStop" in dir(strip):
      self.globalStop(self)  # pylint: disable=no-member
    self.artnet.close()

  def send(self):
    """
    Send the data of myself to the strip
    """
    self.artnet.send(self)

  def clear(self, color=None):
    """
    Clear the entire strip with one color (default: black).
    Color is array: [r, g, b].
    """
    if color and len(color):
      [r, g, b] = color
    else:
      [r, g, b] = [0, 0, 0]
    self.rgb = [[r, g, b] for x in range(self.length)]

  def set(self, index, color, alpha=-1):
    """
    Set led at index to color.
    """
    if ((index >= 0) and (index < self.length)):
      [r, g, b] = color
      if alpha >= 0:
        c = self.get(index)
        if c[0] > 0 and c[1] > 0 and c[2] > 0:
          alpha = float(alpha) / 255.0
          r = int(alpha * r + (1 - alpha) * c[0])
          g = int(alpha * g + (1 - alpha) * c[1])
          b = int(alpha * b + (1 - alpha) * c[2])
          if r > 255:
            r = 255
          if g > 255:
            g = 255
          if b > 255:
            b = 255
      self.rgb[self.length - 1 - index] = [r, g, b]

  def get(self, index):
    """
    Get color of led at index.
    """
    if ((index >= 0) and (index < self.length)):
      [r, g, b] = self.rgb[self.length - 1 - index]
      return [r, g, b]
    else:
      return [0, 0, 0]

  def setm(self, index, colors):
    """
    Set a range of leds starting at index to the specified colors.
    """
    length = len(colors)
    for i in range(length):
      self.set(index + i, colors[i])

  def getm(self, index, length):
    """
    Get the colors of a range of leds starting at index up to given length.
    """
    a = []
    for i in range(length):
      a.append(self.get(index + i))
    return a

  def append(self, color):
    """
    Append a color to the end of the strip.
    """
    self.rgb = [color] + self.rgb
    self.rgb.pop()

  def fade(self, a):
    """
    Fade that strip by a factor a
    """
    for i in range(self.length):
      [r, g, b] = self.rgb[i]
      r = int(float(r) * float(a))
      g = int(float(g) * float(a))
      b = int(float(b) * float(a))
      self.rgb[i] = [r, g, b]

  def print_(self):
    """
    Print strip contents to stdout.
    """
    for i in range(self.length):
      print("strip ", i, self.rgb[i][0], self.rgb[i][1], self.rgb[i][2])
