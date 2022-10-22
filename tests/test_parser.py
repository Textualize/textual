from textual._parser import Parser


def test_read1():
    class TestParser(Parser[str]):
        """A simple parser that reads a byte at a time from a stream."""

        def parse(self, on_token):
            while True:
                data = yield self.read1()
                if not data:
                    break
                on_token(data)

    test_parser = TestParser()
    test_data = "Where there is a Will there is a way!"

    for size in range(1, len(test_data) + 1):
        # Feed the parser in pieces, first 1 character at a time, then 2, etc
        data = []
        for offset in range(0, len(test_data), size):
            for chunk in test_parser.feed(test_data[offset : offset + size]):
                data.append(chunk)
        # Check we have received all the data in characters, no matter the fee dsize
        assert len(data) == len(test_data)
        assert "".join(data) == test_data


def test_read():
    class TestParser(Parser[str]):
        """A parser that reads chunks of a given size from the stream."""

        def __init__(self, size):
            self.size = size
            super().__init__()

        def parse(self, on_token):
            while True:
                data = yield self.read1()
                if not data:
                    break
                on_token(data)

    test_data = "Where there is a Will there is a way!"

    for read_size in range(1, len(test_data) + 1):
        for size in range(1, len(test_data) + 1):
            test_parser = TestParser(read_size)
            data = []
            for offset in range(0, len(test_data), size):
                for chunk in test_parser.feed(test_data[offset : offset + size]):
                    data.append(chunk)
            assert "".join(data) == test_data
