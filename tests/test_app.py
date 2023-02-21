from textual.app import App


def test_batch_update():
    """Test `batch_update` context manager"""
    app = App()
    assert app._batch_count == 0  # Start at zero

    with app.batch_update():
        assert app._batch_count == 1  # Increments in context manager

        with app.batch_update():
            assert app._batch_count == 2  # Nested updates

        assert app._batch_count == 1  # Exiting decrements

    assert app._batch_count == 0  # Back to zero
