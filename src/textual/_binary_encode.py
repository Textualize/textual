"""
An encoding / decoding format suitable for serializing data structures to binary.

This is based on https://en.wikipedia.org/wiki/Bencode with some extensions.

The following data types may be encoded:

- int
- bool
- bytes
- str
- list
- tuple
- dict

"""

from __future__ import annotations


class DecodeError(Exception):
    """A problem decoding data."""


def dump(data: object) -> bytes:
    """Encodes a data structure in to bytes.

    Args:
        data: Data structure

    Returns:
        A byte string encoding the data.
    """

    def encode(datum: object) -> bytes:
        """Recursively encode data.

        Args:
            datum: Data suitable for encoding.

        Raises:
            TypeError: If `datum` is not one of the supported types.

        Returns:
            Encoded data bytes.
        """
        if isinstance(datum, bool):
            return b"b%ie" % int(datum)
        if isinstance(datum, int):
            return b"i%ie" % datum
        if isinstance(datum, bytes):
            return b"%i:%s" % (len(datum), datum)
        if isinstance(datum, str):
            return b"s%i:%s" % (len(datum), datum.encode("utf-8"))
        if isinstance(datum, list):
            return b"l%se" % b"".join(encode(element) for element in datum)
        if isinstance(datum, tuple):
            return b"t%se" % b"".join(encode(element) for element in datum)
        if isinstance(datum, dict):
            return b"d%se" % b"".join(
                b"%s%s" % (encode(key), encode(value)) for key, value in datum.items()
            )

        raise TypeError("Can't encode {datum!r}")

    return encode(data)


def load(encoded: bytes) -> object:
    """Load an encoded data structure from bytes.

    Args:
        encoded: Encoded data in bytes.

    Raises:
        DecodeError: If an error was encountered decoding the string.

    Returns:
        Decoded data.
    """
    position = 0

    max_position = len(encoded)

    def get_byte() -> bytes:
        """Get an encoded byte and advance position.

        Raises:
            DecodeError: If the end of the data was reached

        Returns:
            A bytes object with a single byte.
        """
        nonlocal position
        if position >= max_position:
            raise DecodeError("More data expected")
        character = encoded[position : position + 1]
        position += 1
        return character

    def peek_byte() -> bytes:
        """Get the byte at the current position, but don't advance position.

        Returns:
            A bytes object with a single byte.
        """
        return encoded[position : position + 1]

    def get_bytes(size: int) -> bytes:
        """Get a number of bytes of encode data.

        Args:
            size: Number of bytes to retrieve.

        Raises:
            DecodeError: If there aren't enough bytes.

        Returns:
            A bytes object.
        """
        nonlocal position
        bytes_data = encoded[position : position + size]
        if len(bytes_data) != size:
            raise DecodeError(b"Missing bytes in {bytes_data!r}")
        position += size
        return bytes_data

    def decode_int() -> int:
        """Decode an int from the encoded data.

        Returns:
            An integer.
        """
        int_bytes = b""
        while (byte := get_byte()) != b"e":
            int_bytes += byte
        return int(int_bytes)

    def decode_bool() -> bool:
        """Decode a bool from the encoded data.

        Returns:
            A bool.
        """
        int_bytes = b""
        while (byte := get_byte()) != b"e":
            int_bytes += byte
        return int(int_bytes) == 1

    def decode_bytes(size_bytes: bytes) -> bytes:
        """Decode a bytes string from the encoded data.

        Returns:
            A bytes object.
        """
        while (byte := get_byte()) != b":":
            size_bytes += byte
        bytes_string = get_bytes(int(size_bytes))
        return bytes_string

    def decode_string() -> str:
        """Decode a (utf-8 encoded) string from the encoded data.

        Returns:
            A string.
        """
        size_bytes = b""
        while (byte := get_byte()) != b":":
            size_bytes += byte
        bytes_string = get_bytes(int(size_bytes))
        decoded_string = bytes_string.decode("utf-8", errors="replace")
        return decoded_string

    def decode_list() -> list[object]:
        """Decode a list.

        Returns:
            A list of data.
        """
        elements: list[object] = []
        add_element = elements.append
        while peek_byte() != b"e":
            add_element(decode())
        get_byte()
        return elements

    def decode_tuple() -> tuple[object, ...]:
        """Decode a tuple.

        Returns:
            A tuple of decoded data.
        """
        elements: list[object] = []
        add_element = elements.append
        while peek_byte() != b"e":
            add_element(decode())
        get_byte()
        return tuple(elements)

    def decode_dict() -> dict[object, object]:
        """Decode a dict.

        Returns:
            A dict of decoded data.
        """
        elements: dict[object, object] = {}
        add_element = elements.__setitem__
        while peek_byte() != b"e":
            add_element(decode(), decode())
        get_byte()
        return elements

    DECODERS = {
        b"i": decode_int,
        b"b": decode_bool,
        b"s": decode_string,
        b"l": decode_list,
        b"t": decode_tuple,
        b"d": decode_dict,
    }

    def decode() -> object:
        """Recursively decode data.

        Returns:
            Decoded data.
        """
        decoder = DECODERS.get(initial := get_byte(), None)
        if decoder is None:
            return decode_bytes(initial)
        return decoder()

    return decode()


if __name__ == "__main__":
    tests = [
        False,
        True,
        0,
        1,
        100,
        "Hello",
        b"World",
        [],
        [1, 2, 3],
        ["hello", "world"],
        ["hello", b"world"],
        ("hello", "world"),
        ("hello", b"world"),
        {},
        {"foo": "bar"},
        {"foo": "bar", b"egg": b"baz"},
        [{}],
        [[1]],
        [(1, 2), (3, 4)],
    ]

    from rich import print

    for test in tests:
        print("")
        print(f"Encoding: \t{test!r}")
        encoded = dump(test)
        print(f"Encoded: \t{encoded!r}")
        decoded = load(encoded)
        print(f"Decoded: \t{decoded!r}")
        assert test == decoded
