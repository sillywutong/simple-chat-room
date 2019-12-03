from binascii import unhexlify
from hashlib import md5 as _md5
# long_to_bytes code from: https://stackoverflow.com/questions/8730927/convert-python-long-int-to-fixed-size-byte-array
def long_to_bytes (val, endianness='big'):
    """
    Use :ref:`string formatting` and :func:`~binascii.unhexlify` to
    convert ``val``, a :func:`long`, to a byte :func:`str`.

    :param long val: The value to pack

    :param str endianness: The endianness of the result. ``'big'`` for
      big-endian, ``'little'`` for little-endian.

    If you want byte- and word-ordering to differ, you're on your own.

    Using :ref:`string formatting` lets us use Python's C innards.
    """

    # one (1) hex digit per four (4) bits
    width = val.bit_length()

    # unhexlify wants an even multiple of eight (8) bits, but we don't
    # want more digits than we need (hence the ternary-ish 'or')
    width += 8 - ((width % 8) or 8)

    # format width specifier: four (4) bits per hex digit
    fmt = '%%0%dx' % (width // 4)

    # prepend zero (0) to the width, to zero-pad the output
    s = unhexlify('00') if fmt % val == '0' else unhexlify(fmt % val)

    if endianness == 'little':
        # see http://stackoverflow.com/a/931095/309233
        s = s[::-1]

    return s

def md5(text):
    m = _md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()

class Buffer:
  def __init__(self, data):
    self.data = data
    self.cursor = 0
  
  def read(self, n):
    '''
      read n bytes from byte data
    '''
    b = self.data[self.cursor: self.cursor+n]
    self.cursor += n
    return b
  def read_all(self):
    '''
      read the rest data
    '''
    b = self.data[self.cursor : len(self.data)]
    self.cursor = len(self.data)
    return b
  def is_empty(self):
    return self.cursor == len(self.data)
