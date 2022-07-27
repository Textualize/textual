from textual._partition import partition


def test_partition():
    def is_odd(value: int) -> bool:
        return bool(value % 2)

    assert partition(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == (
        [2, 4, 6, 8, 10],
        [1, 3, 5, 7, 9],
    )

    assert partition(is_odd, [1, 2]) == ([2], [1])
    assert partition(is_odd, [1]) == ([], [1])
    assert partition(is_odd, []) == ([], [])
