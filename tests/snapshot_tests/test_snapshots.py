def test_grid_layout_basic(snap_compare):
    assert snap_compare("docs/examples/guide/layout/grid_layout1.py")


def test_grid_layout_basic_overflow(snap_compare):
    assert snap_compare("docs/examples/guide/layout/grid_layout2.py")


def test_combining_layouts(snap_compare):
    assert snap_compare("docs/examples/guide/layout/combining_layouts.py")


def test_layers(snap_compare):
    assert snap_compare("docs/examples/guide/layout/layers.py")
