from textual._partition import partition


def test_partition():
    def is_odd(value: int) -> bool:
        return bool(value % 2)

    def is_greater_than_five(value: int) -> bool:
        return value > 5

    assert partition(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == (
        [2, 4, 6, 8, 10],
        [1, 3, 5, 7, 9],
    )

    assert partition(is_odd, [1, 2]) == ([2], [1])
    assert partition(is_odd, [1]) == ([], [1])
    assert partition(is_odd, []) == ([], [])

    assert partition(is_greater_than_five, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]) == (
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
    )

    assert partition(is_greater_than_five, [6, 7, 8, 9, 10]) == ([], [6, 7, 8, 9, 10])

    assert partition(is_greater_than_five, [1, 2, 3]) == ([1, 2, 3], [])
