from textual._unique import unique_ordered


def test_unique_ordered():
    """Test result is both unique and the same order as given."""
    assert unique_ordered() == []
    assert unique_ordered([1]) == [1]
    assert unique_ordered([1, 1, 1]) == [1]
    assert unique_ordered([1], [2], [3]) == [1, 2, 3]
    assert unique_ordered([1, 2], [2], [3, 1]) == [1, 2, 3]
    assert unique_ordered([3, 1], [2], [1]) == [3, 1, 2]
    assert unique_ordered([10, 9, 8, 7, 6, 5], [8, 7, 6, 5, 4], [5, 4, 3, 2, 1]) == [
        10,
        9,
        8,
        7,
        6,
        5,
        4,
        3,
        2,
        1,
    ]
