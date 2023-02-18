from textual.app import App


def test_batch_update():
    app = App()
    assert app._batch_count == 0
    with app.batch_update():
        assert app._batch_count == 1
        with app.batch_update():
            assert app._batch_count == 2
        assert app._batch_count == 1
    assert app._batch_count == 0
