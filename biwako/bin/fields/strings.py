from .base import Field


class String(Field):
    def __init__(self, *args, encoding=None, **kwargs):
        ''.encode(encoding)  # Check for a valid encoding
        self.encoding = encoding
        super(String, self).__init__(*args, **kwargs)

    def encode(self, value):
        return value.encode(self.encoding)

    def decode(self, value):
        return value.decode(self.encoding)


class FixedString(String):
    def __init__(self, value, *args, encoding='ascii', **kwargs):
        super(FixedString, self).__init__(*args, encoding=encoding, size=None, **kwargs)
        if isinstance(value, bytes):
            self.encoded_value = value
            self.decoded_value = value.decode(encoding)
        elif isinstance(value, str):
            self.encoded_value = value.encode(encoding)
            self.decoded_value = value
        self.size = len(self.encoded_value)

    def encode(self, value):
        return self.encoded_value

    def decode(self, value):
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.value, value))
        return self.decoded_value

