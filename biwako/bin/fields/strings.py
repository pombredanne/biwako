from .base import Field
from .numbers import Integer
from ..fields import args


class String(Field):
    size = args.Override(default=None)
    encoding = args.Argument(resolve_field=True)
    padding = args.Argument(default=b'\x00')
    terminator = args.Argument(default=b'\x00')

    def read(self, file):
        if self.size is not None:
            return file.read(self.size)

        else:
            # TODO: There's gotta be a better way, but it works for now
            value = b''
            while True:
                data = file.read(1)
                if data == self.terminator:
                    break
                value += data

        return value

    def decode(self, value):
        return value.rstrip(self.terminator).rstrip(self.padding).decode(self.encoding)

    def encode(self, value):
        value = value.encode(self.encoding)
        if self.size is not None:
            value = value.ljust(self.size, self.padding)
        else:
            value += self.terminator
        return value

    def validate(self, obj, value):
        value = value.encode(self.encoding)
        if self.size is not None:
            if len(value) > self.size:
                raise ValueError("String %r is longer than %r bytes." % (value, self.size))


class LengthIndexedString(String):
    def read(self, file):
        size_bytes, size = Integer(size=self.size).read_value(file)
        value_bytes = file.read(size)
        return size_bytes + value_bytes

    def decode(self, value):
        # Skip the length portion of the byte string before decoding
        return value[self.size:].decode(self.encoding)

    def encode(self, value):
        value_bytes = value.encode(self.encoding)
        size_bytes = Integer(size=self.size).encode(len(value_bytes))
        return size_bytes + value_bytes


class FixedString(String):
    def __init__(self, value, *args, encoding='ascii', **kwargs):
        super(FixedString, self).__init__(*args, encoding=encoding, size=None,
                                          padding=b'', terminator=b'', **kwargs)
        self.size = None
        if isinstance(value, bytes):
            # If raw bytes are supplied, encoding is not used
            self.encoded_value = value
            self.decoded_value = value
            self.encoding = None
        elif isinstance(value, str):
            self.decoded_value = value
            self.encoded_value = super(FixedString, self).encode(value)
        self.size = len(self.encoded_value)

    def extract(self, obj):
        value = obj.read(self.size)
        if value != self.encoded_value:
            raise ValueError('Expected %r, got %r.' % (self.encoded_value, value))
        return self.decoded_value

    def encode(self, value):
        if value != self.decoded_value:
            raise ValueError('Expected %r, got %r.' % (self.decoded_value, value))
        return self.encoded_value


class Bytes(Field):
    size = args.Argument() # Must be specified

    def encode(self, value):
        # Nothing to do here
        return value

    def decode(self, value):
        # Nothing to do here
        return value


