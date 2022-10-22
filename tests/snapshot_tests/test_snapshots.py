def test_grid_layout_basic(snap_compare):
    assert snap_compare("docs/examples/guide/layout/grid_layout1.py")


def test_grid_layout_basic_overflow(snap_compare):
    assert snap_compare("docs/examples/guide/layout/grid_layout2.py")


def test_grid_layout_gutter(snap_compare):
    assert snap_compare("docs/examples/guide/layout/grid_layout7_gutter.py")


def test_layers(snap_compare):
    assert snap_compare("docs/examples/guide/layout/layers.py")


def test_horizontal_layout(snap_compare):
    assert snap_compare("docs/examples/guide/layout/horizontal_layout.py")


def test_vertical_layout(snap_compare):
    assert snap_compare("docs/examples/guide/layout/vertical_layout.py")


def test_dock_layout_sidebar(snap_compare):
    assert snap_compare("docs/examples/guide/layout/dock_layout2_sidebar.py")


def test_checkboxes(snap_compare):
    """Tests checkboxes but also acts a regression test for using
    width: auto in a Horizontal layout context."""
    assert snap_compare("docs/examples/widgets/checkbox.py")
